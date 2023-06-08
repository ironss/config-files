#! /usr/bin/python3

# Take a screenshot from an IP-connected oscilloscope using SCPI commands.
# * Converts from BMP to PNG. This reduces file size from 1.4 Mbytes to 20 kbytes.
#   Also saves about 2--3 kbytes, but this is negligible compared with the BMP-PNG
#   saving.
# * Converts from colour to 16-greyscale black on white for better printing.
# * Save to a file with a generated filename that includes timestamp and 
#   oscilloscope details.
# * Updates a symlink to the most-recent screenshot

import io
import datetime
import socket
import zoneinfo

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ExifTags

# Create a map to look up Exif ID from tag-name
_exif_id = { v: k for k, v in PIL.ExifTags.TAGS.items() }


class Instrument:
    _scpi_protocols = {
        ( 'OWON'                 , 'TAO3104'  ) : 'scpi_owon1'    ,
        ( 'KEYSIGHT TECHNOLOGIES', 'DSOX1202A') : 'scpi_keysight1',
        ( 'RIGOL TECHNOLOGIES'   , 'MSO1104Z' ) : 'scpi_rigol1'   ,
    }

    _scpi_protocol_cmds = {
        'scpi_owon1': {
            'screenshot'    : ( b':DAT:WAVE:SCREEN:BMP?\n'  , 2, lambda b: b[4:]   , {
                'greyscale': True,
                'invert'   : True,
            } ),
        },
        'scpi_keysight1': {
            'screenshot'    : ( b':DISP:DATA? BMP\n'        , 1, lambda b: b[10:-1], {
                'greyscale': False,
                'invert'   : False, 
            } ),
        },
        'scpi_rigol1': {
            'screenshot'    : ( b':DISP:DATA? OFF,OFF,PNG\n', 1, lambda b: b[11:-1], {
                'greyscale': False,
                'invert'   : True,
            } ),
        },
    }

    def __init__(self, name, addr, autoid=True):
        self.name = name
        self.addr = addr
        
        self.identity = None
        self.manufacturer = None
        self.model = None
        self.serial = None
        self.firmware_version = None
        self.protocol_name = None
        self.protocol_cmd = None

        if autoid:
            self.identify()
        
        
    def identify(self):
        response = self._query(b'*IDN?\n', timeout=1)
        identity = response.decode().strip()
        parts = identity.split(',')
        if len(parts) == 4:
            self.identity = response
            self.manufacturer, self.model, self.serial, self.firmware_version = parts
            self.manufacturer_abbr = self.manufacturer.split(' ')[0]
            self.protocol_name = self._scpi_protocols[(self.manufacturer, self.model)]
            self.protocol_cmd = self._scpi_protocol_cmds[self.protocol_name]
        else:
            self.identity = None
            self.manufacturer, self.model, self.serial, self.firmware_version = (None, None, None, None)
            self.manufacturer_abbr = None
            self.protocol = None
            self.protocol_cmd = None

    
    def _screenshot_raw(self):
        cmd_details = self.protocol_cmd['screenshot']
        response = self._query(cmd_details[0], cmd_details[1])
        
        if not response:
            return None
        
        img_data = cmd_details[2](response)
        return img_data

    
    def screenshot(self, dt=None, **kwargs):
        kwargs_defaults = {
            'greyscale': True,
            'invert': True,
            'comment_fmt': 'scopeshot {dt:%Y-%m-%d %H:%M:%S%z} {mfr_abbr} {model} {serial}',
            'comment_font_fn': "courbd.ttf",
            'comment_font_size': 12,
            'exif_comment_fmt': 'scopeshot,{dt:%Y-%m-%d_%H.%M.%S%z},{mfr},{model},{serial}',
            'copyright': '(c) RIVIR',
        }

        kargs = kwargs_defaults | self.protocol_cmd['screenshot'][3] | kwargs

        if dt is None:
            dt = datetime.datetime.now(tz=datetime.timezone.utc)      # Force an aware-datetime
        
        img_data = self._screenshot_raw()
        img = PIL.Image.open(io.BytesIO(img_data))

        if kargs['greyscale']:
            img = img.convert('L')

        if kargs['invert']:
            img = PIL.ImageOps.invert(img)

        cmt_text = kargs['comment_fmt'].format(dt=dt.astimezone(), mfr_abbr=self.manufacturer_abbr, model=self.model, serial=self.serial)
        if cmt_text:
            cmt_font = PIL.ImageFont.truetype(kargs['comment_font_fn'], kargs['comment_font_size'])
            cmt_bbox = cmt_font.getbbox(cmt_text)
            cmt_img = PIL.Image.new('L', (cmt_bbox[2], cmt_bbox[3]), color=255)  # White background
            cmt_draw = PIL.ImageDraw.Draw(cmt_img)
            cmt_draw.text((0, 0), cmt_text, 0, cmt_font)                        # Black text, using inverted text as a mask
            cmt_img = cmt_img.rotate(90, expand=1)
            img.paste(cmt_img, (img.size[0]-cmt_img.size[0]-2, img.size[1]-cmt_img.size[1]-2), PIL.ImageOps.invert(cmt_img))
        
        # Write Exif data
        img_exif = img.getexif()
        exif_cmt = kargs['exif_comment_fmt'].format(dt=dt.astimezone(), mfr=self.manufacturer, model=self.model, serial=self.serial)
        if exif_cmt:
            img_exif[_exif_id['UserComment']] = b'\x00'*8 + exif_cmt.encode('UTF8')
        img_exif[_exif_id['DateTimeDigitized']] = '{:%Y-%m-%d %H:%M:%S%z}'.format(dt.astimezone())
        img_exif[_exif_id['Make']] = self.manufacturer
        img_exif[_exif_id['Model']] = self.model
        img_exif[_exif_id['CameraSerialNumber']] = self.serial
        img_exif[_exif_id['Copyright']] = kargs['copyright']
        #img_exif[_exif_id['XResolution']] = kargs['file_resolution']
        #img_exif[_exif_id['YResolution']] = kargs['file_resolution']

        return img
        
    def _query(self, request, timeout=0.1):
        if isinstance(self.addr, tuple):    
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(self.addr)
                sock.setblocking(True)
                sock.settimeout(timeout)

                sock.send(request)
                data = b''
                while True:
                    try:
                        buf = sock.recv(4096)
                    except TimeoutError:
                        break
                    data += buf
                sock.close()
            return data



if __name__ == '__main__':
    import argparse
    import datetime
    import json
    import os

    argparser = argparse.ArgumentParser()
    argparser.add_argument('device', nargs='*', default=["Stephen's Rigol"], help='Instrument name, IP:port or VISA address')

    args = argparser.parse_args()
    xargs = {
        # TODO: Some or all of these should be command-line parameters
        'file_fmt': '{file_dir}/scopeshot-{dt:%Y-%m-%d_%H.%M.%S%z}-{mfr_abbr}-{model}-{serial}.{file_type}',
        'file_type': 'png',
        'file_dir': os.path.join(os.environ['HOME'], 'Pictures'),
        'file_resolution': 120,
        'link_fmt': '{file_dir}/scopeshot.{file_type}',
    }


    # TODO: Read scope-names and addresses from a (JSON?) configuration file
    scopes = {
        "RIVIR OWON"      : (( '192.168.1.72' , 3000 ), ( 'OWON'    , 'TAO3104'  ), '2253142'        ),
        "Aidan's Keysight": (( '192.168.1.112', 5025 ), ( 'Keysight', 'DSOX1201A'), ''             ),
        "Stephen's Rigol" : (( '192.168.1.21' , 5555 ), ( 'Rigol'   , 'MSO1104Z' ), 'DS1ZC194302050' ),
    }

    dt = datetime.datetime.now(tz=datetime.timezone.utc)      # Force an aware-datetime

    for dev in args.device:
        # Look up device-id in the name table
        try:
            scope_addr = scopes[dev][0]
            scope_name = dev
        except KeyError:
            scope_addr = None
            scope_name = None
        
        # TODO: See if it looks like an IP address
        if scope_addr is None:
            continue      

        # TODO: See if it looks like a VISA address
        
        if scope_name is None:
            scope_name = '{}-{}'.format(*scope_addr)
        
        print("identify: {} ({})".format(scope_name, scope_addr))
        scope = Instrument(scope_name, scope_addr)
        if scope.identity is None:
            print("not found: {} ({})".format(scope_name, scope_addr))
            continue

        print("screenshot: {} ({})".format(scope_name, scope_addr))
        screenshot = scope.screenshot(dt)
        
        ofn = xargs['file_fmt'].format(file_dir=xargs['file_dir'], dt=dt.astimezone(), mfr_abbr=scope.manufacturer_abbr, model=scope.model, serial=scope.serial, file_type=xargs['file_type'])

        print('writing: {}'.format(ofn))
        screenshot.save(ofn, dpi=(xargs['file_resolution'], xargs['file_resolution']), exif=screenshot.getexif())

        sfn = xargs['link_fmt'].format(file_dir=xargs['file_dir'], dt=dt, manufacturer=scope.manufacturer, model=scope.model, serial=scope.serial, file_type=xargs['file_type'])
        if sfn:
            os.symlink(ofn, sfn + '.tmp')
            os.rename(sfn + '.tmp', sfn)
        
        print()

