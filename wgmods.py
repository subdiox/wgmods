import urllib
import json
import sys
import html
import http.cookiejar

mod_id_list = [16, 22, 736, 1138]

def progressbar(blocknum, blocksize, totalsize):
  readsofar = blocknum * blocksize
  if totalsize > 0:
    if totalsize < readsofar:
      percent = 100
      readsofar = totalsize
    else:
      percent = readsofar * 1e2 / totalsize
    s = "\r%5.1f%% %*d / %d" % (
      percent, len(str(totalsize)), readsofar, totalsize)
    sys.stderr.write(s)
    if readsofar >= totalsize:  # near the end
      sys.stderr.write("\n")
  else:  # total size is unknown
    sys.stderr.write("read %d\n" % (readsofar,))

for mod_id in mod_id_list:

  cookies = http.cookiejar.CookieJar()
  opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
  opener.addheaders = [('Cookie', 'userrealm=sg')]

  with opener.open(f'https://wgmods.net/{mod_id}/') as res:
    res_body = res.read().decode('utf-8')
    mod_name_index = res_body.find('"view-mod__header__title"')
    if mod_name_index >= 0:
      mod_name = html.unescape(res_body[mod_name_index:].split('>')[1].split('<')[0])
    token_index = res_body.find('X-CSRFToken')
    if token_index >= 0:
      token = res_body[token_index + 15:token_index + 79]

  opener.addheaders = [('X-CSRFToken', token), ('X-Requested-With', 'XMLHttpRequest')]

  with opener.open(f'https://wgmods.net/api/mods/get_versions/{mod_id}/') as res:
    mod_all_json = json.loads(res.read().decode('utf-8'))

  mod_json = mod_all_json[0]
  game_title = mod_json['game_short_title']
  mod_version = mod_json['version']
  game_version = mod_json['game_version']['version']
  download_url = mod_json['download_url']
  file_name = mod_json['version_file_original_name']
  file_size = mod_json['version_file_size']

  print(f'{mod_name} (ID: {mod_id})')
  print(f' - Version: {mod_version}')
  print(f' - Supported Game Version: {game_title} {game_version}')
  print(f' - Download URL: {download_url}')
  print(f' - File Name: {file_name}')
  print(f' - File Size: {file_size}')

  urllib.request.urlretrieve(download_url, file_name, progressbar)
  print('')
