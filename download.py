def download_url(s, url, save_path, chunk_size=16*1024):
    r = s.get(url, stream=True)
    name = r.headers.get("Content-Disposition").split("filename=")[1].replace("\"", "")
    with open(save_path+name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            filename = fd.write(chunk)
        return name