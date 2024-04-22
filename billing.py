#!/usr/bin/env python

import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner

from hx711_calibrate import Calibration

import requests
import json
from requests.structures import CaseInsensitiveDict

runner = None

CALIBRATION_FILE = 'calibration_data.txt'
flag = 0
ratio = -1363.992


id_product = 1
list_label = []
list_weight = []
count = 0
final_weight = 0
taken = 0

a = 'Apple'
b = 'Banana'
l = 'Lays'
c = 'Coke'


def now():
    return round(time.time() * 1000)

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)
signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python billing.py <path_to_model.eim>')
def find_weight():
    global CALIBRATION_FILE
    calibration = Calibration(CALIBRATION_FILE=CALIBRATION_FILE)
    return calibration.get_weight()

def post(label, price, final_rate, taken):
    global id_product
    url = "https://automaticbilling.herokuapp.com/product"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data_dict = {
        "id": id_product,
        "name": label,
        "price": price,
        "units": "units",
        "taken": taken,
        "payable": final_rate
    }
    data = json.dumps(data_dict)
    resp = requests.post(url, headers=headers, data=data)
    print(resp.status_code)
    id_product = id_product + 1
    time.sleep(1)
    list_label = []
    list_weight = []
    count = 0
    final_weight = 0
    taken = 0
def rate(final_weight, label, taken):
    print("Calculating rate")
    if label == a:
        print("Calculating rate of", label)
        final_rate_a = final_weight * 0.01
        price = 10
        post(label, price, final_rate_a, taken)
    elif label == b:
        print("Calculating rate of", label)
        final_rate_b = final_weight * 0.02
        price = 20
        post(label, price, final_rate_b, taken)
    elif label == l:
        print("Calculating rate of", label)
        final_rate_l = 1
        price = 1
        post(label, price, final_rate_l, taken)
    else:
        print("Calculating rate of", label)
        final_rate_c = 2
        price = 2
        post(label, price, final_rate_c, taken)
def list_com(label, final_weight):
    global count
    global taken
    if final_weight > 2:
        list_weight.append(final_weight)
        if count > 1 and list_weight[-1] > list_weight[-2]:
            taken = taken + 1
    list_label.append(label)
    count = count + 1
    print('count is', count)
    time.sleep(1)
    if count > 1:
        if list_label[-1] != list_label[-2]:
            print("New Item detected")
            print("Final weight is", list_weight[-1])
            rate(list_weight[-2], list_label[-2], taken)



def main(argv):
    global flag
    global final_weight

    if flag == 0:
        find_weight()
        flag = 1
    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']

            next_frame = 0  # limit to ~10 fps here

            for res, img in runner.classifierPicamera():
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)

                print('classification runner response', res)

                if "classification" in res["result"].keys():
                    print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                    for label in labels:
                        score = res['result']['classification'][label]
                        if score > 0.9:
                            final_weight = find_weight()
                            list_com(label, final_weight)
                            if label == a:
                                print('Apple detected')
                            elif label == b:
                                print('Banana detected')
                            elif label == l:
                                print('Lays deteccted')
                            else:
                                print('Coke detected')
                    print('', flush=True)
                next_frame = now() + 100
        finally:
            if (runner):
                runner.stop()


if __name__ == "__main__":
    main(sys.argv[1:])
