import math

import av
import numpy
import cv2
from av.video.stream import VideoStream
from PIL import Image


def rgb_to_y(pics, width, height):
    y = []

    for k, pic in enumerate(pics):
        y.append([])
        print(k)
        for i in range(0, height):
            y[k].append([])
            for j in range(0, width):
                blue, green, red = (pic[i* height + j])
                value = (int)(0.299 * red + 0.587 * green + 0.114 * blue)
                y[k][i].append(value)

    return y



def expected_value(y, a, height, width):
    value = 0
    for i in range(0, height):
        for j in range(0, width):
            value += y[a][i][j]
    return (float)(value / (height * width))

def sigma(y, a , height, width): # возвращает сигму и мат ожидание, чтоб 2 раза не считать мат ожидание
    value = 0
    expected_val = expected_value(y, a , height, width)
    for i in range(0, height):
        for j in range(0, width):
            value += (y[a][i][j] - expected_val) ** 2
    return math.sqrt(value / (height * width-1)), expected_val

def correlation(y, a, b, sigma_a, ev_a, sigma_b, ev_b, height, width): #ev_a - expected value
    val = 0
    for i in range(0, height):
        for j in range(0, width):
            val += (y[a][i][j] - ev_a) * (y[b][i][j] - ev_b)
    return (float) (val/ (width * height *sigma_a * sigma_b))





def auto_correlation(y, height, width):
    correlation_coeff = []
    #----------------------------
    expected_values = []
    sigmas = []
    for i in range(0, len(y)):
        sig, expected_val = sigma(y, i, height, width)
        sigmas.append(sig)
        expected_values.append(expected_val)
    # вычисление мат ожидания и сигмы для каждого кадра
    print("progress (" + str(len(y)) + ") = ", end =' ')
    for a in range (0, len(y)):
        correlation_coeff.append([])
        print(a,end=' ')
        for b in range(0, len(y)):
            value = correlation(y, a, b, sigmas[a],expected_values[a] ,sigmas[b],expected_values[b], height, width)
            correlation_coeff[a].append(value)
    return correlation_coeff


def fun1(filename):
    array_list = []
    input_container = av.open(filename)
    input_packets = input_container.demux()
    #print(input_packets.stream.codec)
    mas_of_pixels = []
    width = 0
    height = 0
    for packet in input_packets:
        if isinstance(packet.stream, VideoStream):
            # Получим все кадры пакета
            frames = packet.decode()
            for raw_frame in frames:
                cur_image = raw_frame.to_rgb().to_image()
                mas_of_pixels.append(list(cur_image.getdata()))  # массив пикселей для всех картинок
                width, height = cur_image.size
    y = rgb_to_y(mas_of_pixels, width, height)
    correl = auto_correlation(y, height, width)
    file = open('correlation3.txt', 'w')
    min = 1
    for i in range(0, len(correl)):
        for j in range(0, len(correl[i]) - 1):
            file.write(str(correl[i][j]) + ',')
            if correl[i][j] < min:
                min = correl[i][j]
        file.write(str(correl[i][j]))
        file.write('\n')
    file.close()
    print(min)

def fun2(filename):
    input_container = av.open(filename)
    stream = input_container.streams.video[0] #поток
    height = stream.height
    width = stream.width
    format = stream.pix_fmt
    codec = stream.codec_context.name
    rate = stream.average_rate

    frames = []
    for fr in input_container.decode(stream):
        frames.append(numpy.array(fr.to_image()))

    result = av.open('out.avi', 'w')
    result_stream = result.add_stream(codec, rate=rate)
    result_stream.height = height
    result_stream.width = width
    result_stream.pix_fmt = format
    for i in range(0,len(frames)):
        image = av.VideoFrame.from_image(Image.fromarray(frames[len(frames)-i - 1], mode='RGB'))
        for p in result_stream.encode(image):
            result.mux(p)
    result.close()

def fun3(filename1, filename2):
    input_container = av.open(filename1)
    stream = input_container.streams.video[0]  # поток из видео 1
    height = stream.height
    width = stream.width
    format = stream.pix_fmt
    codec = stream.codec_context.name
    rate = stream.average_rate

    frames1 = []
    for fr in input_container.decode(stream):
        frames1.append(numpy.array(fr.to_image()))
    input_container = av.open(filename2)
    stream = input_container.streams.video[0]  # поток из видео 2
    frames2 = []
    for fr in input_container.decode(stream):
        frames2.append(numpy.array(fr.to_image()))

    result = av.open('out.avi', 'w')
    result_stream = result.add_stream(codec, rate=rate)
    result_stream.height = height
    result_stream.width = width
    result_stream.pix_fmt = format
    for fr in frames1:
        image = av.VideoFrame.from_image(Image.fromarray(fr, mode='RGB'))
        for p in result_stream.encode(image):
            result.mux(p)
    for fr in frames2:
        image = av.VideoFrame.from_image(Image.fromarray(fr, mode='RGB'))
        for p in result_stream.encode(image):
            result.mux(p)
    result.close()


def dop(filename):
    input_container = av.open(filename)
    stream = input_container.streams.video[0] #поток
    height = stream.height
    width = stream.width
    format = stream.pix_fmt
    codec = stream.codec_context.name
    rate = stream.average_rate
    new_size = (width*2, height*2)
    frames = []
    for fr in input_container.decode(stream):
        res = cv2.resize(numpy.array(fr.to_image()), new_size, interpolation=cv2.INTER_CUBIC) #ресайз и интерполяция пустых пикселей
        #INTER_CUBIC -бикубическая интерполяция по окрестности пикселя 4x4
        #INTER_LANCZOS4 -интерполяция Ланцоса по окрестности 8x8 пикселей
        frames.append(res)

    result = av.open('out.avi', 'w')
    result_stream = result.add_stream(codec, rate=rate)
    result_stream.height = height*2
    result_stream.width = width*2
    result_stream.pix_fmt = format
    for fr in frames:
        image = av.VideoFrame.from_image(Image.fromarray(fr, mode='RGB'))
        for p in result_stream.encode(image):
            result.mux(p)
    result.close()


def main():
     #fun1('LR1_1.AVI')
    #fun2('LR1_1.AVI')
    #fun3('LR1_1.AVI', 'LR1_2.AVI')
    dop('LR1_1.AVI')

if __name__ == '__main__':
    main()




