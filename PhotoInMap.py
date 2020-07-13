import os
import re
import base64
from glob import glob
from PIL import Image
import exifread
import folium

m = folium.Map(location=[43.6532, -79.3832])

# add comment: God bless America

class PhotoInMap(object):

  def __init__(self):
    self.source_dir = 'img'
    self.target_dir = 'output'
    self.source_filenames = glob('{}/*'.format(self.source_dir))

  def embed(self):
    self.compress()
    return self.extract()

# compress the photos
  def compress(self):
    if not os.path.exists(self.target_dir):
        os.makedirs(self.target_dir)

    for filename in self.source_filenames:
        with Image.open(filename, mode='r') as im:
            width, height = im.size
            new_width = int(width /4)
            new_height = int(height /4)
            resized_im = im.resize((new_width, new_height))
            output_filename = filename.replace(self.source_dir, self.target_dir)
            resized_im.save(output_filename)

# extract info from photo and plug them into the map
  def extract(self):
    for filename in self.source_filenames:
      with open(filename,'rb') as f:
          contents = exifread.process_file(f)
          # lat
          lon_ref = contents["GPS GPSLongitudeRef"].printable
          lon = contents["GPS GPSLongitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
          lon = float(lon[0]) + float(lon[1]) / 60 +  float(lon[2]) / 3600
          if lon_ref != "E":
              lon = lon * (-1)

          # lon
          lat_ref = contents["GPS GPSLatitudeRef"].printable
          lat = contents["GPS GPSLatitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
          lat = float(lat[0]) + float(lat[1]) / 60 +  float(lat[2]) / 3600
          if lat_ref != "N":
              lat = lat * (-1)

          # date
          date_shoot = contents["Image DateTime"]

          encoded = base64.b64encode(open(filename.replace(self.source_dir, self.target_dir),'rb').read())

          text = '<p> time: %s </p><img src="data:image/jpeg;base64,{}">' % date_shoot

          html = text.format
          iframe = folium.IFrame(html=html(encoded.decode("utf-8")), width=500, height=300)
          popup = folium.Popup(iframe, max_width=500)
          icon = folium.Icon(color="red", icon="ok")
          marker = folium.Marker(location=[lat, lon], popup=popup, icon=icon)
          marker.add_to(m)
    return m


if __name__ == '__main__':
  a = PhotoInMap()
  my = a.embed()
  my.save("mymap.html")
