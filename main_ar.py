# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 11:25:00 2019

@author: Катрина
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
import heapq #очередь с приоритетами (двоичная куча)
#специальная библиотека для работы со словарями, списками и т.п.
import collections as coll
import pickle #для сохранения словаря в файл

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

#функция шифрования
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

#функция дешифрования
def decodirovanie(zakod, alf): #функция декодирования 
    decod_str=[] #раскодированные символы, но в виде массива
    bin_ch="" #строка для накопления двоичных символов
    for b_ch in zakod: #для каждого символа из закодированной строки
        bin_ch+=b_ch #двоичная строка
        for keys in alf: #для ключей из алфавита (словаря)
            if alf.get(keys)==bin_ch: #если значение ключа равно значению двоичной строи
                decod_str.append(keys) #записываем символ (ключ из словаря) в массив для раскодирования
                bin_ch="" #обнуляем двоичную строку
    stroka="".join(decod_str) #формирование строки раскодированной
    return stroka #декодированная строка
       
class Main_arhiv(QMainWindow): #класс, где храняться все действия
    def __init__(self): #служебная функция инициализации,загрузка окна
         QMainWindow.__init__(self)
         loadUi("design.ui",self) #файл с расположение кнопок и виджета (должны находиться в одной папке)
         self.setWindowTitle('Архиватор/распаковщик')
         
         self.button_arhiv.clicked.connect(self.arhiv) #кнопка для архивирования
         self.button_raspakovka.clicked.connect(self.raspakovka) #кнопка для распраковки
         
         self.action_2.triggered.connect(self.showDialog) #файл/открыть файл для архивирования
         self.action_3.triggered.connect(self.sohran) #файл/сохранить файл после распаковки
         
    def showDialog(self): #открытие файла через диалог
        
        fname = QFileDialog.getOpenFileName(self, 'открыть файл', None, "Текстовый документ (*.txt)")[0] 
        f = open(fname, 'r')
        with f:
            data = f.read()
            self.okno_texta.setText(data)    
            
    def sohran(self): #сохрание файла через диалог
        f1=self.okno_file.toPlainText()
        if f1=="" or f1==" ":
            QMessageBox.information(self, 'Предупреждение', "Введите не пустое имя файла!!!!")
        else:
            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',f1, "Текстовый документ (*.txt)")
            f=self.okno_texta.toPlainText()
            with open(name[0],"w") as fout: #байтовая запись в файл
                fout.write(f)
            msgbox = QMessageBox(QMessageBox.Information, "Сообщение", "Сохранение прошло успешно!!. \nИмя вашего файла: %s" % f1, QMessageBox.Ok)
            msgbox.exec_()
            
    def arhiv(self): #архивирование
        f=self.okno_texta.toPlainText() #окошко с текстом
        f1=self.okno_file.toPlainText() #окошко с названием файла
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
        if f1=="" or f1==" ":
            QMessageBox.information(self, 'Предупреждение', "Введите не пустое имя файла!!!!")
        else:
            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',f1, "Текстовый документ (*.txt)")
            with open(name[0],"wb") as fout: #байтовая запись в файл
                fout.write(bytearray(codec))
            with open('slovar.txt','wb') as m_file_cod: #байтовая запись файл словаря
                pickle.dump(cod1,m_file_cod) #запись специализированного объекта в файл
            msgbox = QMessageBox(QMessageBox.Information, "Сообщение", "Архивирование прошло успешно. \nИмя вашего файла: %s" % f1, QMessageBox.Ok)
            msgbox.exec_()
            
    def raspakovka(self): #распаковка
        fname = QFileDialog.getOpenFileName(self, 'открыть файл', None, "Текстовый документ (*.txt)")[0]
        with open(fname, "rb") as m_file_decod: #открытие файла на байтовое чтение
            de_codec = m_file_decod.read() #байтовое чтение из файла
            shufr=list(de_codec.decode('utf-8')) #массив из закодированных символов
        for i in range(len(shufr)):#для каждого элемента зашифрованного
            shufr[i]=ord(shufr[i]) #код символа в ASCII
            shufr[i]=bin(shufr[i])[2:] #перевод этого когда из десятичного числа в двоичное, [2:] нужно, чтобы убрать впереди обозначение 0b
        for i in range(len(shufr)): #для каждого двоичного числа 
            while len(shufr[i])%8!=0: #пока разрядность двоичного числа не кратна 8
                shufr[i]="0"+shufr[i] #Добавляем вперёд ноль
        if shufr!=[]: #если массив со символами не пустой
            bit=int(shufr.pop(0),base=2) #первый байт извлекает, переводится в десятичное число и удаляется, этот байт обозначает - сколько нулей в конец добавили
        else:
            bit=0 #иначе 0
        zas="".join(shufr) #закодированная из 0 и 1
        zas=zas[:(len(zas)-bit)] #удаляем последние добавленные нули в строке
        #открытие словаря
        with open('slovar.txt','rb') as m_file_dec: #байтовое чтение файла
            cod2=pickle.load(m_file_dec) #загружает объект из файла
        s=decodirovanie(zas, cod2) #декодирование
        self.okno_texta.setText(s)
        QMessageBox.information(self, 'Сообщение', "Распаковка прошла успешно!!!")
###-----------------------------------------------------------------------------------------
#вызов окна 
if __name__ == '__main__': 
   app = QApplication(sys.argv) 
   form = Main_arhiv() 
   form.show() 
   app.exec() 