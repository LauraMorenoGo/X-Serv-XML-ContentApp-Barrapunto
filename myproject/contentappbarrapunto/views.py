from django.shortcuts import render
from .models import Pages
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import string
import urllib.request

noticia = ""

def normalize_whitespace(text):
    string = ""
    return string.join(text)

class myContentHandler(ContentHandler):

    def __init__ (self):
        self.inItem = False
        self.inContent = False
        self.theContent = ""
        self.fichero = open("noticias.html", "w")
        self.link = ""
        self.title = ""
        self.noticia = ""

    def startElement (self, name, attrs):
        if name == 'item':
            self.inItem = True
        elif self.inItem:
            if name == 'title':
                self.inContent = True
                self.title = self.theContent
            elif name == 'link':
                self.inContent = True
            
    def endElement (self, name):
        if name == 'item':
            self.inItem = False
        elif self.inItem:
            if name == 'title':
                self.title = normalize_whitespace(self.theContent)
                self.inContent = False
                self.theContent = ""
            elif name == 'link':
                self.link = normalize_whitespace(self.theContent)			
                self.noticia = "<li>Titulo <a href=" + self.link + ">" + self.title + "</a></li>"
                self.fichero.write(self.noticia)		
                self.inContent = False
                self.theContent = ""

    def characters (self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars
            
def process():
    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)
    u = urllib.request.urlopen('http://barrapunto.com/index.rss')
    theParser.parse(u)
    return theHandler.noticia

print ("Parse complete")

@csrf_exempt

def descarga(request):
    global noticia
    noticia = process()
    return HttpResponse("<br>Las noticias se han actualizado</br>")

def processbarrapunto(request, rec):
    if request.method == "GET":
        try:
            lista = Pages.objects.get(name=rec)
            return HttpResponse(lista.page + "<br>" + noticia)
        except Pages.DoesNotExist:
            return HttpResponseNotFound("La página / " + rec + " no ha sido encontrada")
    elif request.method == "PUT":
        try:
            cuerpo = request.body
            lista = Pages.objects.create(name=rec, page=cuerpo)
            lista.save()
            return HttpResponse("Nueva fila creada")
        except:
            return HttpResponseNotFound("Se ha producido un error")
