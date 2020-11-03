# -*-coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   Giulio Fattori 30.10.2020                                             *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsFeature,
                       QgsFeatureRequest,
                       QgsField,
                       QgsFields,
                       QgsGeometry,
                       QgsPoint,
                       QgsPointXY,
                       QgsWkbTypes,
                       QgsProject,
                       QgsVectorLayer,
                       QgsExpression,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterExpression,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterDefinition,
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingParameterFileDestination,
                       )
import processing
import datetime
from pathlib import Path


class HTML_Table_with_css_ProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    Algorithm that fractions a poligon in n parts.
    """
    INPUT_L   = 'INPUT_L'    #layer dati
    INPUT_F   = 'INPUT_F'    #campi per html
    INPUT_D   = 'INPUT_D'    #dimensione in pixel width foto
    GROUP_BY  = 'GROUP_BY'   #espressione filtro
    INPUT_T   = 'INPUT T'    #titolo pagina
    INPUT_I   = 'INPUT_I'    #icona
    INPUT_S   = 'INPUT_S'    #foglio di style
    INPUT_ABS = 'INPUT_ABS'  #percorso relativo si/no
    
    OUTPUT = 'OUTPUT'
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return HTML_Table_with_css_ProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'HTML Table with css'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('HTML Table with css')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('HTML')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'HTML'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("<mark style='color:black; font-size: 8px'><strong>Version 2.60 02.11.2020</strong></mark>\n\
        Produce un file da utilizzare come sorgente html in una cornice HTML del composer\n\
        <mark style='color:blue'><strong>OPZIONI</strong></mark>\n\
        <i>- Filtro sui campi\n\
        - Foglio di stile css\n\
        - Dimensione foto e icona dell'intestazione\n\
        - Percorsi assoluti / relativi</i>\n\
        <mark style='color:black'><strong>NOTA BENE</strong></mark>\n\
        <mark style='color:black'><strong>I campi con immagini devono contenere il nome con estensione es: image.jpg</strong></mark>\n\
        <strong>I campi con immagini possono contenere anche il percorso relativo o assoluto\n\
        <strong>Le dimensioni delle immagini possono essere in tutte le unità di misura HTML\n\
        <strong>Trascinando i campi nel selettore campi per HTML è possibile riordinarli\n\
        <strong>Tutte le impostazioni del foglio di stile devono essere riferite all'elemento 'Table'\n\
        <strong>Selezionare riferimenti relativi consente il trasferimento del progetto, in tal caso:\n\
        <mark style='color:green'><strong>LE CARTELLE ED I RELATIVI FILE DEVONO ESSERE NELLA CARTELLA DI PROGETTO</strong></mark>\n\
        <p><mark style='color:red'>Per includere nel progetto il file HTML e il CSS relativo incollare il sorgente HTML\
        nella casella<i><strong>'Sorgente'</i></strong> delle proprietà della cornice HTML</mark></p>\n\
        ")

    
    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        # We add the point input vector features source
        #QgsProcessingFeatureSourceDefinition 
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_L,
                self.tr('Input sorgente dati'),
                [QgsProcessing.TypeMapLayer],
                "C:/Users/Delta/Desktop/SCRIPT GIS/Test HTML/elenco_test.csv"
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_F,
                self.tr('Selezionare i campi da inserire nel file Html'),
                allowMultiple = True,
                defaultValue = ['id','Data','Nome_Foto','Descrizione','Foto_0'],
                parentLayerParameterName=self.INPUT_L
            )
        )
        
        self.addParameter(
            QgsProcessingParameterExpression(
                self.GROUP_BY,
                self.tr('Espressione filtro'),
                #defaultValue= " ""id"" in ('1','10','20')",
                optional = True,
                parentLayerParameterName=self.INPUT_L
            )
        )
        
        self.addParameter(
            QgsProcessingParameterExpression(
                self.INPUT_T,
                self.tr('Titolo pagina'),
                #defaultValue='Assoluto',
                optional = True,
                parentLayerParameterName=self.INPUT_L
            )
        )
        
        # We add the input icon source
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_I,
                'Icona Gruppo',
                behavior=QgsProcessingParameterFile.File, fileFilter='Image file (*.gif; *.jpeg; *.jpg; *.png; *.svg)',
                defaultValue = 'C:\\Users\\Delta\\Desktop\\SCRIPT GIS\\Test HTML\\icone\\Nur1.jpg',
                optional = True
            )
        )
        
        # We add the input css
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_S,
                'Foglio di stile CSS',
                behavior=QgsProcessingParameterFile.File, fileFilter='Css file (*.css)',
                defaultValue = "C:\\Users\\Delta\\Desktop\\SCRIPT GIS\\Test HTML\\css\\grey.css",
                optional = True
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_D,
                'Dimensioni icona Gruppo e foto [base x altezza in pt, px, mm, auto]',
                '25px; 25px; auto; 10%'
            )
        )

        # We add a file output of type HTML
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Tabella HTML'),
                'HTML files (*.html)',
            )
        )
        
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INPUT_ABS,
                'Percorsi file relativi',
                0
            )
        )
        
    
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        sourceL = self.parameterAsSource(
            parameters,
            self.INPUT_L,
            context)
        
        sourceF = self.parameterAsMatrix(
            parameters,
            self.INPUT_F,
            context)
        
        filtro = self.parameterAsString(
            parameters,
            self.GROUP_BY,
            context)
        
        titolo = self.parameterAsString(
            parameters,
            self.INPUT_T,
            context)
    
        html = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context)
         
        source_path = self.parameterAsString(
            parameters,
            self.INPUT_L,
            context)
            
        f_base = self.parameterAsString(
            parameters,
            self.INPUT_D,
            context)
        
        icona = self.parameterAsString(
            parameters,
            self.INPUT_I,
            context)
        
        fogliocss = self.parameterAsString(
            parameters,
            self.INPUT_S,
            context)
            
        rel_path = self.parameterAsBool(
            parameters,
            self.INPUT_ABS,
            context)
        
        #FASE #01 - cerco la path del progetto
        if QgsProject.instance().homePath():
            path_proj = QgsProject.instance().homePath()
            #windowizzo la path quale che sia
            path_proj = str(Path(path_proj))
            #rimuovo geopakage: se presente
            path_proj = path_proj.replace('geopackage:','')
            #print('path proj ', path_proj)
        else:
            feedback.reportError('WARNING NO PROJECT PATH: the html file may not work correctly\n')
            #print('***** no project path')
            path_proj = ''
        #tolgo %20 e metto spazio 
        path_proj = path_proj.replace('%20',' ')
        
        #FASE #02 - cerco la path del file di input
        path_file = (self.parameterDefinition('INPUT_L').valueAsPythonString(parameters['INPUT_L'], context))
        path_file = path_file[1:path_file.rfind('/')+1]
        if 'memory' in path_file:
            path_file = ''
            #print('temporary file')
        else:
            #windowizzo la path quale che sia
            path_file = str(Path(path_file))
            #print('file path ', path_file)
        #tolgo %20 e metto spazio 
        path_file = path_file.replace('%20',' ')
        
        #FASE #03 - scelgo la path da usare tra le due: prioritaria quella di progetto
        if path_proj:
            path_dir = path_proj
            if path_proj not in path_file and path_file != '':
                feedback.reportError('WARNING PATH FILE ' + path_file)
                feedback.reportError('OUTSIDE PROJECT PATH ' + path_proj)
                feedback.reportError('MOST LIKELY IT WON''T WORK' + '\n')
            elif path_file == '':
                feedback.reportError('WARNING TEMPORARY LAYER WITHOUT PATH\n')
        else:
            path_dir = path_file
            if path_dir:
                feedback.reportError('WARNING use the path of the input file ' + path_dir + '\n')
            else:
                feedback.reportError('WARNING TEMPORARY LAYER WITHOUT PATH\n')
        
        #FASE #04 - controllo se si sta salvando file con percorsi relativi nella cartella di progetto
        if path_dir not in str(Path(html)) and 'processing' not in str(Path(html)):
             #print('html ', str(Path(html)))
             feedback.reportError('WARNING HTML WITH RELATIVE PATH SAVED OUTSIDE THE PROJECT PATH DOES NOT WORK PROPERLY\n')
        if 'processing' in str(Path(html)):
             #print('html ', str(Path(html)))
             feedback.reportError('WARNING TEMPORARY HTML WORK PROPERLY ONLY WITH ABSOLUTE PATH\n')
             
        #FASE #05 - controllo se icona e css sono entro la cartella progetto
        if fogliocss and (path_dir not in fogliocss):
            feedback.reportError('WARNING css PATH OUTSIDE PROJECT PATH: the html file may not work correctly\n')
        if icona and path_dir not in icona:
            feedback.reportError('WARNING icon PATH OUTSIDE PROJECT PATH: the html file may not work correctly\n')
        
        #FASE #06 - aggiungo terminatore di percorso se non è un file temporaneo
        if path_dir != '':
            path_dir = path_dir + '\\'
        #print('Final path ', path_dir)
        
        
        #FASE #07 - modifica se csv in input
        if source_path.find(".csv"):
            source_path = 'file:///' + source_path[0:source_path.rfind('/')+1]
         
        #FASE #08 recupero dimensioni foto e icona, titolo e riordino a causa di un bug 
        wi, hi, wf, hf = f_base.split(';')
        titolo = titolo.replace('\"','')
        
        intestazione = titolo.replace('"','')
        intestazione = titolo.replace('\'','')
        
        #riordino campi come da selezione per bug 
        cleanlist = []
        [cleanlist.append(x) for x in sourceF if x not in cleanlist]
        sourceF = cleanlist
        
        #FASE #09 - inizializzo variabile per barra % esecuzione script
        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / sourceL.featureCount() if sourceL.featureCount() else 0
        
        #FASE #10 - filtra dati se richiesto
        if len (filtro) > 0:
            request = QgsFeatureRequest(QgsExpression(filtro))
            features = sourceL.getFeatures(request)
        else:
            features = sourceL.getFeatures()
        
        
        #FASE #11 - produco il file in uscita
        with open(html, 'w') as output_file:
            # write header
            line = '<html>\r'
            output_file.write(line)
            
            #FASE #11.01 - se richiesto inserisco foglio css
            if fogliocss:
                if not rel_path or 'processing' in html:
                    fogliocss = 'file:///' + fogliocss
                else:
                    fogliocss = str(Path(fogliocss))
                    fogliocss = fogliocss.replace(path_dir,'')
                line = '<head>\r<link rel="stylesheet" href="'+ fogliocss + '">\r</head>'
                output_file.write(line)
            
            #FASE #11.02 - se richiesto inserisco icona e titolo
            if icona or titolo:
                line = '<div>'
                if icona:
                    if not rel_path or 'processing' in html:
                        icona = 'file:///' + icona
                    else:
                        icona = str(Path(icona))
                        icona = icona.replace(path_dir,'')
                    line = '<img src="' + icona +'" style="width:' + wi + ';height:' + hi + ';">'
                    output_file.write(line)
                    line = ''
                if titolo:
                    if icona:
                        line = line + '<b>' + '&nbsp&nbsp' + titolo + '</b>'
                    else:
                        line = line + '<b>' + titolo + '</b>'
                    output_file.write(line)
                line = '</div>'
                output_file.write(line)
                line = None
            
            #FASE #11.03 - compongo tabella
            line = '<table class="Table">\r<thead>\r<tr>\r'
            output_file.write(line)
            
            #titoli colonne
            line = ''.join(('<th style="width:auto">'+ str(name)+ '</<th>\r') for name in sourceF) + '</tr>\r'
            output_file.write(line)
            
            line = '</thead>\r<tbody>\r'
            output_file.write(line)
            
            #righe tabella
            for current, f in enumerate(features):
                line = '<tr>\r'
                output_file.write(line)
                
                for name in sourceF:
                    #controllo se si tratta di una immagine
                    try:
                        img_type = f[name].split(".")
                        img_type = img_type[len(img_type)-1]
                        #print('img ok ', name, f[name], img_type)
                    except:
                        img_type = ''
                        #print('img no ', name, f[name], img_type)
                        
                    #se è un'immagine e/o ha un percorso
                    if img_type in ["JPEG","jpeg","JPG","jpg","PNG","png"]:
                        #se non è un file temporaneo o non voglio riferimenti relativi
                        if not rel_path or 'processing' in html:
                            img_name = 'file:///'
                            if path_dir not in str(Path(f[name])):
                                img_name = img_name + path_dir
                            img_name = img_name + f[name]
                        else:
                            #se voglio riferimenti relativi
                            img_name = str(Path(f[name]))
                            img_name = img_name.replace(path_dir,'')
                        line = ''.join('<td><center><img src ='+ "'" + img_name + "'" + 'width="' + wf + '" height="' + hf + '"></center></td>\r')
                    else:
                        try:
                            line = ''.join('<td>'+f[name].toString("dd.MM.yyyy")+ '</td>\r')
                        except:
                            line = ''.join('<td>'+ str(f[name]) + '</td>\r')
                    output_file.write(line)
                
                line = '</tr>\r'
                output_file.write(line)

                # Update the progress bar
                feedback.setProgress(int(current * total))
    
            line = '</tbody>\r</table>\r</html>'
            output_file.write(line)
            
        return {self.OUTPUT: html}