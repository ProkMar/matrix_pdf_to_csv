import os
import cv2
import fitz
from pylibdmtx import pylibdmtx


def process_file(work_directory, input_file, output_file, **kwargs):

    output_dir = os.path.join(work_directory, 'output_csv')
    input_path = os.path.join(work_directory, input_file)
    output_path = os.path.join(output_dir, output_file)
    temp_dir = os.path.join(work_directory, 'temp')

    csv_file = open(output_path, 'w', encoding='utf-8')

    pdfIn = fitz.open(input_path)
    page_count = pdfIn.page_count

    # Полистаем страницы
    for pg in range(page_count):

        # Выберем страницу
        page = pdfIn[pg]
        zoom_x = 2
        zoom_y = 2
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        temp_file_name = os.path.join(temp_dir, 'temp.png')

        pix.save(temp_file_name)
        img = cv2.imread(temp_file_name)
        border = cv2.copyMakeBorder(
            img,
            kwargs['top'],
            kwargs['bottom'],
            kwargs['left'],
            kwargs['right'],
            cv2.BORDER_CONSTANT,
            None,
            value=0  # [255, 255, 255]
            )
        decode_data = pylibdmtx.decode(border)
        for i in range(len(decode_data)):
            decode_str = decode_data[i].data.decode(
                'utf-8', errors='strict').replace('\x1d', '')
            csv_file.write(f'{decode_str}\n')
        print(f'Page {pg+1} of {page_count}')
    csv_file.close()

    pdfIn.close()


def make_dirs(work_directory):
    path_output_directory = os.path.join(work_directory, 'output_csv')

    if not os.path.exists(path_output_directory):
        os.mkdir(path_output_directory)

    path_temp_directory = os.path.join(work_directory, 'temp')
    if not os.path.exists(path_temp_directory):
        os.mkdir(path_temp_directory)


def process_files(work_directory, files_dict, **kwargs):
    for input_file, output_file in files_dict.items():
        print(f'{input_file} to {output_file}')
        process_file(work_directory, input_file, output_file, **kwargs)
        print()


def get_pdf_files_list(work_directory):
    import os

    files_dict = dict()
    with os.scandir(work_directory) as file:
        for entry in file:
            source_name = entry.name
            split_file_name = os.path.splitext(source_name)
            if len(split_file_name) == 2 and split_file_name[1] == '.pdf':
                dest_name = f'{split_file_name[0]}.csv'
                files_dict[source_name] = dest_name

    return files_dict


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Не указан обязательный аргумент - каталог с файлами pdf.')
        raise ValueError

    work_directory = sys.argv[1]
    files_dict = get_pdf_files_list(work_directory)
    make_dirs(work_directory)

    top = 0
    bottom = 1372
    left = 0
    right = 197

    process_files(
        work_directory,
        files_dict,
        **{
            'top': top,
            'bottom': bottom,
            'left': left,
            'right': right
            }
        )
