import requests
from tqdm import tqdm
import json
import datetime



class VkUser:
    url = 'https://api.vk.com/method/'
    token_Vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    version = '5.131'
    params = {
        'access_token': token_Vk,
        'v': version
    }

    def __init__(self, user_id=None):
        self.info_foto_list = []
        if user_id is not None:
            self.user_id = user_id
        else:
            self.user_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']


    def photos_get(self, count=None):
        photos_get_url = self.url + 'photos.get'
        if count is not None:
            counter = count
        else:
            counter = 5
        photos_get_params = {
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'count': counter,
            'rev': '1'
            }
        res = requests.get(photos_get_url, params={**self.params, **photos_get_params})
        info_foto_dict = res.json()
        return info_foto_dict

    def conv_dict_list(self, information_dict):
        foto_list = []
        for dict_ in information_dict['response']['items']:
            dict_foto = {}
            dict_foto['date'] = datetime.datetime.fromtimestamp(dict_['date']).strftime('%d.%m.%Y %H.%M.%S')
            dict_foto['likes'] = dict_['likes']['count']
            example = 0
            for var_url in dict_['sizes']:
                size = var_url['height'] * var_url['width']
                if size > example:
                    example = size
                    dict_foto['url'] = var_url['url']
                    dict_foto['size'] = var_url['type']
            foto_list.append(dict_foto)

        info_foto_list = []
        num = len(foto_list)
        for i in range(num - 1):
            dict_ = foto_list.pop()
            for string in foto_list:
                if string['likes'] == dict_['likes']:
                    dict_['file-name'] = '(' + str(dict_['date']) + ')' + str(dict_['likes']) + '.jpg'
                    break
                else:
                    dict_['file-name'] = str(dict_['likes']) + '.jpg'

            info_foto_list.append(dict_)

        last_dict = foto_list.pop()
        last_dict['file-name'] = str(last_dict['likes']) + '.jpg'
        info_foto_list.append(last_dict)
        return info_foto_list

    def create_list_with_requested_information(self, count=None):
        self.info_foto_list = self.conv_dict_list(self.photos_get(count))
        return

    def create_json(self):
        name_file = 'info_foto'
        info_list = self.info_foto_list
        for string in info_list:
            del string['likes'], string['date'], string['url']
        with open(name_file + '.json', "w") as f:
            json.dump(info_list, f, ensure_ascii=False, indent=4)
        return info_list



class YaUser:
    def __init__(self, token: str):
        self.token = token
        self.directory_upload = ''

    def create_folder(self):
        directory = 'folder_foto'
        response = requests.put(
            "https://cloud-api.yandex.net/v1/disk/resources",
            params={
                        "path": directory
            },
            headers={
                    "Authorization": f"OAuth {self.token}"
            }
            )
        self.directory_upload = directory
        if 'message' in response.json():
            print(f'Указанная папка на Яндекс диске была создана ранее')
        elif 'method' in response.json():
            print(f'Папка на Яндекс диске создана успешно')
        return directory


    def upload(self, user):
        if isinstance(user, VkUser):
            for load in tqdm(user.info_foto_list, desc='Идет загрузка фото', leave=False):
                file_name = load['file-name']
                file_url = load['url']
                response = requests.post(
                    "https://cloud-api.yandex.net/v1/disk/resources/upload",
                    params={
                        "path": f'{self.directory_upload}/{file_name}',
                        'url': file_url
                    },
                    headers={
                    "Authorization": f"OAuth {self.token}"
                    }
                )
                response.raise_for_status()
        print(f'Фотографии загружены')
        return


    def copying_photos_to_disk(self, user):
        if isinstance(user, VkUser):
            user.create_list_with_requested_information()
            self.create_folder()
            self.upload(user)
            user.create_json()
            print(f'\nПрограмма завершена успешно!')
            return


begemot_korovin = VkUser()
admin = YaUser('token_Ya')

admin.copying_photos_to_disk(begemot_korovin)
