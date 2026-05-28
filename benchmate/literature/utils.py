import os
import tarfile

import requests

def reconstruct_abstract(inverted_index):
    """
    reconstruct the abstract of the paper because openalex only returns an inverted index
    :param inverted_index:
    :return:
    """
    if inverted_index is None:
        return None
    else:
        pos_to_token = {}
        for token, positions in inverted_index.items():
            for p in positions:
                pos_to_token[p] = token
        return " ".join(
            pos_to_token[p] for p in sorted(pos_to_token)
        )

def extract_pdfs_from_tar(file, destination, base_name):
    """
    extract all pdf files from a tar.gz file to a destination folder and return the paths to the extracted pdf files
    this is there to process pmc tar.gz files
    :param file: downloaded tar.gz file
    :param destination: where to extract the pdf files
    :return: a list of paths to the extracted pdf files
    """

    if not os.path.exists(destination):
        raise FileNotFoundError("{} does not exist.".format(destination))
    try:
        if file.endswith(".tar.gz"):
            read_str="r:gz"
        elif file.endswith(".tar.bz2"):
            read_str="r:bz2"
        elif file.endswith(".zip"):
            read_str="r:zip"
        else:
            read_str="r"

        paths=[]
        with tarfile.open(file, read_str) as tar:
            pdf_members = [
                m for m in tar.getmembers()
                if m.isfile() and m.name.lower().endswith(".pdf")
            ]
            if not pdf_members:
                return []
            for i, member in enumerate(pdf_members, start=1):
                # Naming logic
                if len(pdf_members) == 1:
                    filename = f"{base_name}.pdf"
                else:
                    filename = f"{base_name}_{i}.pdf"

                out_path = os.path.join(destination, filename)
                f = tar.extractfile(member)
                if f is None:
                    continue
                with open(out_path, "wb") as out_f:
                    out_f.write(f.read())
                paths.append(out_path)
        return paths


    except FileNotFoundError:
        print(f"Error: File not found: {file}")
        return None

    except tarfile.ReadError:
        print(f"Error: Could not open or read {file}. It might be corrupted or not a valid tar.gz file.")
        return None


def download_tar(download_link, file):
    """
    download the pmc tar file to destination file
    :param download_link: web link to download tar file
    :param file: file to write the tar file into
    :return: write/download tar file to file
    """
    response=requests.get(download_link, stream=True)
    response.raise_for_status()
    if response.status_code==200: #check get response, is there an error from server side is the link correct
        try:
            with open(file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192): #1MB chunk downloads
                    f.write(chunk)
            return None
        except Exception as e:
            raise RuntimeError('Could not download tar file: {}'.format(e)) from e
    else:
        return response.raise_for_status()

