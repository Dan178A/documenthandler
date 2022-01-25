# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
from pydoc import doc
import sys
import warnings
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QFont , QTextCharFormat , QColor, QBrush ,QTextCursor ,QTextBlockFormat , QTextFormat ,QTextDocument
from PySide2.QtQml import QQmlApplicationEngine , QQmlFile , QQmlFileSelector ,QQmlEngine
from PySide2.QtCore import QObject, Slot, Signal, QFileInfo, QCoreApplication, QSize, Qt, QFile , QTextCodec , QString
import pandas as pd
import json


class DocumentHandler(QObject):
        def __init__(self):
            QObject.__init__(self)
        global m_document
        global m_cursorPosition
        global m_selectionStart
        global m_selectionEnd 
        m_document = None
        m_cursorPosition = -1
        m_selectionStart = 0
        m_selectionEnd = 0
        documentChanged =  Signal() 
        cursorPositionChanged =  Signal()
        selectionStartChanged =  Signal()
        selectionEndChanged =  Signal()
        fontFamilyChanged =  Signal()
        textColorChanged =  Signal()
        alignmentChanged =  Signal()
        boldChanged =  Signal()
        italicChanged =  Signal()
        underlineChanged =  Signal()
        fontSizeChanged =  Signal()
        textChanged =  Signal()
        fileUrlChanged =  Signal()
        loaded =  Signal()
        error=  Signal()


def document(self):
    return m_document
def setDocument(document,m_document,self):
    if document is m_document:
        return
    m_document = document
    self.documentChanged.emit()


def cursorPosition(self):
    return m_cursorPosition
def setCursorPosition(position,self,m_cursorPosition):
    if position == m_cursorPosition:
        return
    m_cursorPosition = position
    reset()
    self.cursorPositionChanged.emit()


def selectionStart(self):
    return m_selectionStart
def setSelectionStart(position,self,m_selectionStart):
    if position == m_selectionStart:
        return
    m_selectionStart = position
    self.selectionStartChanged.emit()


def selectionEnd(self):
    return m_selectionEnd
def setSelectionEnd(position,self,m_selectionEnd):
    if position == m_selectionEnd:
        return
    m_selectionEnd = position
    self.selectionEndChanged.emit()



def fontFamily(self):
    cursor = textCursor()
    if cursor.isNull(self):
        return QString()
    format = cursor.charFormat()
    return format.font().family()
def setFontFamily(family,self):
    format = QTextCharFormat()
    format.setFontFamily(family)
    mergeFormatOnWordOrSelection(format)
    self.fontFamilyChanged.emit()


def textColor(self):
    cursor = textCursor()
    if cursor.isNull(self):
        return QColor(Qt.black)
    format = cursor.charFormat()
    return format.foreground().color()
def setTextColor(color,self):
    format = QTextCharFormat()
    format.setForeground(QBrush(color))
    mergeFormatOnWordOrSelection(format)
    self.textColorChanged.emit()

def alignment(self):
    cursor = textCursor()
    if cursor.isNull(self):
        return Qt.AlignLeft
    return textCursor().blockFormat().alignment()
def setAlignment(alignment,self):
    format = QTextBlockFormat()
    format.setAlignment(alignment)
    cursor = textCursor()
    cursor.mergeBlockFormat(format)
    self.alignmentChanged.emit()


def bold(self):
    cursor = textCursor()
    if cursor.isNull(self):
        return False
    return textCursor().charFormat().fontWeight() == QFont.Bold
def setBold(bold,self):
    format = QTextCharFormat()
    format.setFontWeight(QFont.Bold if bold else QFont.Normal)
    mergeFormatOnWordOrSelection(format)
    self.boldChanged.emit()


def italic(self):
    cursor = textCursor()
    if cursor.isNull(self):
        return False
    return textCursor().charFormat().fontItalic()
#part2
def setItalic(italic,self):
    format = QTextCharFormat()
    format.setFontItalic(italic)
    mergeFormatOnWordOrSelection(format)
    self.italicChanged.emit()


def underline(self):
    cursor = textCursor()
    if cursor.isNull(self):
        return False
    return textCursor().charFormat().fontUnderline()
def setUnderline(underline,self):
    format = QTextCharFormat()
    format.setFontUnderline(underline)
    mergeFormatOnWordOrSelection(format)
    self.underlineChanged.emit()


def fontSize(self):
    cursor = textCursor()
    if cursor.isNull(self):
        return 0
    format = cursor.charFormat()
    return format.font().pointSize()
def setFontSize(size,self):
    if size <= 0:
        return
    cursor = textCursor()
    if cursor.isNull(self):
        return
    if not cursor.hasSelection(self):
        cursor.select(QTextCursor.WordUnderCursor)
    if cursor.charFormat().property(QTextFormat.FontPointSize).toInt() == size:
        return
    format = QTextCharFormat()
    format.setFontPointSize(size)
    mergeFormatOnWordOrSelection(format)
    self.fontSizeChanged.emit()


def fileName(self,m_fileUrl,QStringLiteral):
    filePath = QQmlFile.urlToLocalFileOrQrc(m_fileUrl)
    fileName = QFileInfo(filePath).fileName()
    if fileName.isEmpty(self):
        return QStringLiteral("untitled.txt")
    return QString(fileName)


def fileType(self):
    return QFileInfo(fileName()).suffix()


def fileUrl(self, m_fileUrl,):
    return m_fileUrl
def load(fileUrl,self, m_fileUrl):
    if fileUrl is m_fileUrl:
        return
    engine = QQmlEngine()
    if engine == None:
        warnings() << "load() called before DocumentHandler has QQmlEngine"
        return
    path = QQmlFileSelector.get(engine).selector().select(fileUrl)
    fileName = QQmlFile.urlToLocalFileOrQrc(path)
    if QFile.exists(fileName):
        file = QFile(fileName)
        if file.open(QFile.ReadOnly):
            data = file.readAll()
            codec = QTextCodec.codecForHtml(data)

            if doc == textDocument():
                doc.setModified(False)
            self.loaded.emit(codec.toUnicode(data))
            reset()
        m_fileUrl = fileUrl
        self.fileUrlChanged.emit()
def saveAs(fileUrl,self,m_fileUrl,tr):
    doc = textDocument()
    if doc == None:
        return
    filePath = fileUrl.toLocalFile()
    isHtml = QFileInfo(filePath).suffix().contains(("htm"))
    file = QFile(filePath)
    if not file.open(QFile.WriteOnly | QFile.Truncate | (QFile.NotOpen if isHtml else QFile.Text)):
        self.error.emit(tr("Cannot save: ") + file.errorString())
        return
    file.write((doc.toHtml() if isHtml else doc.toPlainText()).toUtf8())
    file.close()
    if fileUrl is m_fileUrl:
        return
    m_fileUrl = fileUrl
    self.fileUrlChanged.emit()
def reset(self):
    self.fontFamilyChanged.emit()
    self.alignmentChanged.emit()
    self.boldChanged.emit()
    self.italicChanged.emit()
    self.underlineChanged.emit()
    self.fontSizeChanged.emit()
    self.textColorChanged.emit()


def textCursor(self):
    doc = textDocument()
    if doc == None:
        return QTextCursor()
    cursor = QTextCursor(doc)
    if m_selectionStart != m_selectionEnd:
        cursor.setPosition(m_selectionStart)
        cursor.setPosition(m_selectionEnd, QTextCursor.KeepAnchor)
    else:
        cursor.setPosition(m_cursorPosition)
    return QTextCursor(cursor)
def textDocument(self):
    if not m_document:
        return None
    return m_document.textDocument()
def mergeFormatOnWordOrSelection(format,self):
    cursor = textCursor()
    if not cursor.hasSelection():
        cursor.select(QTextCursor.WordUnderCursor)
    cursor.mergeCharFormat(format)