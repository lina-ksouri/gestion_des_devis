#!/usr/bin/python3
# coding: utf-8

from docxtpl import DocxTemplate
from PyPDF2 import PdfFileMerger
import sys
import os
import comtypes.client

PATH = "../common/"

def fill_devis_values (client, tel, mail, number, date_dem, date_liv, dist, vol, date, adresse1, adresse2, e1, e2, escale, prix, vers1, vers2, vers3):

    template_values = {}
    template_values["client"] = client
    template_values["tel"] = tel
    template_values["mail"] = mail
    template_values["number"] = number
    template_values["date_dem"] = date_dem
    template_values["date_liv"] = date_liv
    template_values["dist"] = dist
    template_values["v"] = vol
    template_values["date"] = date
    template_values["adresse1"] = adresse1
    template_values["adresse2"] = adresse2
    template_values["e1"] = e1
    template_values["e2"] = e2
    template_values["escale"] = escale
    template_values["prix"] = prix
    template_values["vers1"] = vers1
    template_values["vers2"] = vers2
    template_values["vers3"] = vers3
    
    return template_values
    
def NT_Devis_Create ():
    
    # get template values
    name_in = PATH + "DEVIS-1.docx"
    name_out = PATH + "DEVIS-1-modified.docx"
    values = fill_devis_values("Nassim", "0733333333", "nassim@gmail.com", "2020112233", "01/01/2020", "02/02/2020", "50", "100", "12/12/2020", "", "", "", "", "", "500", "10", "10", "123")
    wdFormatPDF = 17
    print ("STEP 1 ..")
    
    # Fill the word template
    document = DocxTemplate(name_in)
    document.render(values)
    document.save(name_out)
    print ("STEP 2 ..")
    
    # Convert word to pdf (part1)
    part1_name = PATH + "DEVIS-1.pdf"
    inFile = os.path.abspath(name_out)
    outFile = os.path.abspath(part1_name)
    word = comtypes.client.CreateObject('Word.Application')
    doc = word.Documents.Open(inFile)
    doc.SaveAs(outFile, FileFormat=wdFormatPDF)
    doc.Close()
    word.Quit()
    print ("STEP 3 ..")
    
    # add pdf page 2
    part2_name = PATH + "DEVIS-2.pdf"
    result = PATH + "DEVIS.pdf"
    pdfs=[part1_name, part2_name]
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))  
    with open(result, 'wb') as fout:
        merger.write(fout)
    print ("Success !")