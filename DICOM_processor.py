from __future__ import print_function
import urllib.request  # python3
import os
import pydicom
from os.path import abspath, join, isdir
from shutil import copyfile, move
import glob
from matplotlib import pyplot as plt


def get_dcm_from_url(url="http://www.example.com/dicom_files/dicom_file.dcm"):
    head, filename = os.path.split(url)
    if filename.endswith(".dcm"):
        full_dcm_name = join(os.getcwd(), filename)
        urllib.request.urlretrieve(url, full_dcm_name)
        hierarchical_saving(full_dcm_name, filename, 'move')
    else:
        print('The downloaded file "' + filename + '" is not a dcm file!')


def hierarchical_saving(full_dcm_name, filename, copy_or_move='copy'):
    # print(full_dcm_name)
    ds = pydicom.dcmread(full_dcm_name)
    hierarchy_fullpath = join(os.getcwd(), 'categorized_data', str(ds.PatientName), str(ds.StudyInstanceUID), str(ds.SeriesInstanceUID))
    if not os.path.exists(hierarchy_fullpath):
        os.makedirs(hierarchy_fullpath)
    if copy_or_move == 'copy':
        copyfile(full_dcm_name, hierarchy_fullpath + '/' + filename)
    elif copy_or_move == 'move':
        move(full_dcm_name, hierarchy_fullpath + '/' + filename)


def get_metadata_list():
    data_path = join(os.getcwd(), 'DICOM_files')
    directory = os.fsencode(data_path)
    if os.path.exists("hierarchy_list.txt"):
        os.remove("hierarchy_list.txt")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".dcm"):
            full_dcm_name = join(data_path, filename)
            print(full_dcm_name)
            ds = pydicom.dcmread(full_dcm_name)
            with open("hierarchy_list.txt", "a") as myfile:
                myfile.write(str(ds.PatientName) + ' ' + str(ds.StudyInstanceUID) + ' ' + str(ds.SeriesInstanceUID) + ' ' + filename + '\n')
            hierarchical_saving(full_dcm_name, filename, 'copy')


def generate_patients_details():
    top_folder = join(os.getcwd(), 'categorized_data')
    if isdir(top_folder):
        if os.path.exists("patients_details.txt"):
            os.remove("patients_details.txt")
        dirlist = [item for item in os.listdir(top_folder) if isdir(join(top_folder, item))]
        for patient in dirlist:
            print('getting details for patient: ' + patient)
            full_dcm_name = abspath(glob.glob(top_folder + '/' + patient + '/*/*/*.dcm')[0])
            ds = pydicom.dcmread(full_dcm_name)
            with open("patients_details.txt", "a") as myfile:
                myfile.write(str(ds.PatientName) + ' ' + str(ds.PatientAge) + ' ' + str(ds.PatientSex) + '\n')
    else:
        print("The folder: '" + top_folder + "' doesn't exist!")


def recursively_extract_hospitals():
    top_folder = join(os.getcwd(), 'categorized_data')
    if isdir(top_folder):
        hospitals_list = []
        for filename in glob.glob(top_folder + '/**/*.dcm', recursive=True):
            full_dcm_name = abspath(filename)
            ds = pydicom.dcmread(full_dcm_name)
            hospitals_list.append(str(ds.InstitutionName))
        final_hospitals_list = sorted(set(hospitals_list))
        print("Total number of " + str(len(final_hospitals_list)) + " hospitals:")
        print(final_hospitals_list)
    else:
        print("The folder: '" + top_folder + "' doesn't exist!")


def explore_DICOM_tags(patientName):
    tag_list = ['0008,0013', '0008,0032', '0020,0012', '0020,0013']  # ['InstanceCreationTime','AcquisitionTime','AcquisitionNumber','InstanceNumber']
    top_folder = join(os.getcwd(), 'categorized_data', patientName)
    new_tag_list = []
    for tag in tag_list:
        l1 = list(tag.split(',')[0])
        l2 = list(tag.split(',')[1])
        l1[1] = 'x'; l2[1] = 'x'
        new_tag = ''.join(l1) + ',' + ''.join(l2)
        new_tag_list.append(new_tag)
    filename_list = []; InstanceCreationTime = []; AcquisitionTime = []; AcquisitionNumber = []; InstanceNumber = []
    for filename in glob.glob(top_folder + '/**/*.dcm', recursive=True):
        full_dcm_name = abspath(filename)
        ds = pydicom.dcmread(full_dcm_name)
        head, filename = os.path.split(full_dcm_name)
        print(filename[:-4])
        filename_list.append(filename[:-4])  # x values
        InstanceCreationTime.append(ds[new_tag_list[0].split(',')[0], new_tag_list[0].split(',')[1]].value)
        AcquisitionTime.append(ds[new_tag_list[1].split(',')[0], new_tag_list[1].split(',')[1]].value)
        AcquisitionNumber.append(ds[new_tag_list[2].split(',')[0], new_tag_list[2].split(',')[1]].value)
        InstanceNumber.append(ds[new_tag_list[3].split(',')[0], new_tag_list[3].split(',')[1]].value)
    # print(str(filename_list) + '\n' + str(InstanceCreationTime) + '\n' + str(AcquisitionTime) + '\n' + str(AcquisitionNumber) + '\n' + str(InstanceNumber))
    plot_subject_DICOM_tags(filename_list, InstanceCreationTime, AcquisitionTime, AcquisitionNumber, InstanceNumber)


def plot_subject_DICOM_tags(x, y1, y2, y3, y4):  # filename_list(x), InstanceCreationTime(y1), AcquisitionTime(y2), AcquisitionNumber(y3), InstanceNumber(y4)
    plt.subplot(2, 1, 1)
    plt.plot(x, y1, 'o-', label='InstanceCreationTime')
    plt.plot(x, y2, 'x-', label='AcquisitionTime')
    plt.title('Instance Creation & Acquisition Time')
    plt.ylabel('Time (HH:MM:SS)')
    plt.legend(loc='upper left')

    plt.subplot(2, 1, 2)
    plt.plot(x, y3, 'o-', label='AcquisitionNumber')
    plt.plot(x, y4, 'x-', label='InstanceNumber')
    plt.xlabel('file name')
    plt.ylabel('Identifier')
    plt.legend(loc='upper left')

    plt.show()
