# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 11:25:00 2019

@author: Катрина
"""

import sys
#import math
#import numpy as np
#import numpy.ma as ma   #маски
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import heapq #очередь с приоритетами (двоичная куча)
#специальная библиотека для работы со словарями, списками и т.п.
import collections as coll
import pickle #для сохранения словаря в файл
#import os #для размера файла

#узлы для создания нового узла со суммированной частотой
class New_rib(coll.namedtuple("New_rib",["l","r"])): #специальный кортеж, который имеет имя
    def walk(self,cod,sep): #рекурсивная функция, добавляющая 0 или 1 к новому ребру (листу)
        self.l.walk(cod,sep + "0") #левый
        self.r.walk(cod,sep + "1") #правый

#класс, отвечающий за символ
#так используется для случая пустой строки или с одним или одинаковым символом        
class List(coll.namedtuple("List",["ch"])): 
    def walk(self,cod,sep):
        cod[self.ch]=sep or "0" #возвращает разделитель (например, пустая строка) или 0 (во втором cлучаи и одним символом
 
def codirovanie(str_files): #функция кодирования по коду Хаффмана
    heap=[] #массив для будущего создания кучи (очереди)
    CC=coll.Counter(str_files) #расчёт частоты употребления символов
    for sim, chast in CC.items(): #CC.items() возвращает пары (ключ, значение) в данном случаи - символ и частоту
        heap.append((chast,len(heap),List(sim))) #добавляем частоту, длину массива на каждом проходе (она будет уникальна), сам символ
    heapq.heapify(heap) #Превращает массив в кучу (очередь)
    n=len(heap) #длина кучи
    while len(heap)>1: #если ещё не все узлы пройдены
        chast1, n1, l = heapq.heappop(heap) #первый минимум по частоте - левый узел (вершина),вынимаем из кучи, сохраняем значение его и удаляем
        chast2, n2, r = heapq.heappop(heap)  #второй минимум по частоте - правый узел (вершина),вынимаем из кучи, сохраняем значение его и удаляем
        heapq.heappush(heap,(chast1+chast2,n,New_rib(l,r))) #в кучу heap помещаем элемент, который является родителе для минимальных узлов, найденных ранее, частота суммируется
        n+=1 #увеличиваем количество узлов в дереве
    cod={} #словарь с кодовыми словами полученными
    if heap: #для кучи, если она не пустая
        [(chast,n,root)]=heap #определим корень построенного дерева (последний узел)
        root.walk(cod,"") #от корня формируется словарь с кодовыми словами
    return cod #алфавит: символ и его код
       
class Transport_main(QMainWindow): #класс, где храняться все действия
    def __init__(self): #служебная функция инициализации,загрузка окна
         QMainWindow.__init__(self)
         loadUi("design.ui",self) #файл с расположение кнопок и виджета (должны находиться в одной папке)
         
         self.button_arhiv.clicked.connect(self.arhiv) #при нажатии на кнопку "пересчитать" происходит пересчёт
         #self.button_raspakovka.clicked.connect(self.decodirovanie) #при нажатии на кнопку "решить" происходит поиск решения и считается целевая функция
         #global f
         
         
    def arhiv(self):
        #global f
        #with open('huff.txt') as files: #открытие файла на чтение
            #f=files.read() #вытаскиваем значения из файла и преобразуем в строку
         # поле для ввода текста
        #f = self.okno_texta.toPlainText()
        #f = self.textEdit.toPlainText()
        f=self.okno_texta.toPlainText()
        f1=self.okno_file.toPlainText()
        print(f)
        print(f1)
        h=".txt"
        f1=f1+h
        cod1 = codirovanie(f) #вызов алгоритма кодирования
        zakod = "".join(cod1[ch] for ch in f) #Сборка строки из списка с разделителем который перед точкой, без этого выведет только словарь
        nyl=0 #объявляем переменную для подсчёта количества нулей в конце, для кратности 8
        #побитовая запись в файл
        while len(zakod)%8!=0: #пока строка некратна 8
            zakod=zakod+"0" #добавляем нули в конец
            nyl+=1 #количество добавленных нулей 
        nyl=bin(nyl)[2:] #переводим в двоичное число
        while len(nyl)%8!=0: #если полученное число двоичное число не 8-ми битное
            nyl="0"+nyl #добавляем нули вперёд
        if zakod!="": #если не пустая строка
            zakod=nyl+zakod #записываем это двоичное число в начало
        z1=[zakod[i:i+8] for i in range(0, len(zakod), 8)] #делим строку по 8 бит (1 байту) - получаем массив
        for i in range(len(z1)): #полученные значения в массиве
            z1[i]=int(z1[i],2) #переводим в десятичное число
            z1[i]=chr(z1[i]) #переводим в символы ascii
        z2="".join(z1) #делаем из массива символов строку
        codec=list(z2.encode('utf-8'))#кодирует строку в байтстроку, используя зарегистрированный кодек (кодировку)
        with open(f1,"wb") as fout: #байтовая запись в файл
            fout.write(bytearray(codec))
        #запись словаря в файл
        print("")
        print(codec)
        with open('slovar.txt','wb') as m_file_cod: #байтовая запись файл словаря
            pickle.dump(cod1,m_file_cod) #запись специализированного объекта в файл
        self.reply = QMessageBox.information(self, 'Сообщение',
            "В таблицах имеются пустные ячейки или где-то есть не число.\nПроверьте ещё раз на заполненость.")
            
            
###-----------------------------------------------------------------------------------------
#вызов окна 
if __name__ == '__main__': 
   app = QApplication(sys.argv) 
   form = Transport_main() 
   form.show() 
   app.exec() 