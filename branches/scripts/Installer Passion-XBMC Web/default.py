﻿
# GET AND PRINT ALL STATS OF SCRIPT
TEST_PERFORMANCE = False

UNIT_TEST        = False
DEV_TEST         = True


# script constants
__script__       = "Installer Passion-XBMC"
if DEV_TEST: __script__ += " Web"

__plugin__       = "Unknown"
__author__       = "Team Passion-XBMC"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Installer%20Passion-XBMC/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"

__version__      = "pre-2.0"
__statut__       = "DevHD; Beta 1" #(dev,svn,release,etc)

# don't edit __date__ and __svn_revision__ 
# use svn:keywords http://svnbook.red-bean.com/en/1.4/svn.advanced.props.special.keywords.html
__date__         = "$Date$".split()[ 1 ]
__svn_revision__ = "$Revision$".replace( "Revision", "" ).strip( "$: " )


#Modules general
import os
import sys
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui

# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

# Shared resources
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
PLATFORM_LIBRARIES = os.path.join( BASE_RESOURCE_PATH, "platform_libraries" )
LIBS               = os.path.join( BASE_RESOURCE_PATH, "libs" )
GUI_LIBS           = os.path.join( LIBS, "GUI" )
CONTENTS_LIBS      = os.path.join( LIBS, "sources" )

# append the proper platforms folder to our path, xbox is the same as win32
sys.path.append( os.path.join( PLATFORM_LIBRARIES, ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ] ) )
# append the proper libs folder to our path
sys.path.append( LIBS )
# append the proper GUI folder to our path
sys.path.append( GUI_LIBS )
# append the proper sources contents ("PassionXbmcWeb","PassionXbmcFtp","XbmcZone",etc...) folder to our path
for content in os.listdir( CONTENTS_LIBS ):
    try: sys.path.append( os.path.join( CONTENTS_LIBS, content ) )
    except: print_exc()

# recompile all modules, but script start slowly
#from compileall import compile_dir
#compile_dir( os.path.join( BASE_RESOURCE_PATH, "libs" ), force=True, quiet=True )


#modules custom
from specialpath import *
import script_log as logger


#frost: changer la langue par default pour l'anglais, car de cette maniere on ai pas obliger de rejouter le strings manquant dans les autres language
#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE. ( ex: __language__( 0 ) = id="0" du fichier strings.xml )
#__language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString
__language__ = xbmc.Language( ROOTDIR ).getLocalizedString
LANGUAGE_IS_FRENCH = ( xbmc.getLanguage().lower() == "french" )

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# Info version (deprecated)
__version_l1__ = __language__( 700 )#"version"
__version_r1__ = __version__
__version_l2__ = __language__( 707 )#"date"
__version_r2__ = __date__
__version_l3__ = __language__( 708 )#"SVN"
__version_r3__ = str( __svn_revision__ )

# team credits
__credits_l1__ = __language__( 702 )#"Developpeurs"
__credits_r1__ = "Frost & Seb & Temhil"
__credits_l2__ = __language__( 703 )#"Conception Graphique"
__credits_r2__ = "Frost & Jahnrik & Temhil"
__credits_l3__ = __language__( 709 )#"Langues"
__credits_r3__ = "Frost & Kottis & Temhil"
__credits_l4__ = __language__( 706 )#"Conseils et soutien"
__credits_r4__ = "Alexsolex & Shaitan"


def MAIN():
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "Lanceur".center( 85 ) )
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )

    try:
        # INITIALISATION CHEMINS DE FICHIER LOCAUX
        import CONF
        config = CONF.ReadConfig()

        DIALOG_PROGRESS.update( -1, __language__( 101 ), __language__( 110 ) )
        if not config.getboolean( 'InstallPath', 'pathok' ):
            # GENERATION DES INFORMATIONS LOCALES
            CONF.SetConfiguration()

        # VERIFICATION DE LA MISE A JOUR
        import CHECKMAJ
        try:
            from utilities import Settings
            CHECKMAJ.UPDATE_STARTUP = Settings().get_settings().get( "update_startup", True )
            del Settings
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        if CHECKMAJ.UPDATE_STARTUP:
            DIALOG_PROGRESS.update( -1, __language__( 102 ), __language__( 110 ) )
        CHECKMAJ.go()
        del CHECKMAJ

        config = CONF.ReadConfig()
        del CONF

        dialog_error = False
        if not config.getboolean( 'Version', 'UPDATING' ):
            try:
                # LANCEMENT DU SCRIPT
                try:
                    import Home
                    DIALOG_PROGRESS.close()
                    HomeAction = Home.show_home()
                except:
                    print_exc()
                    HomeAction = "error"

                if HomeAction == "error":
                    import MainGui
                    MainGui.show_main()
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
                print_exc()
                dialog_error = True
        else:
            # LANCEMENT DE LA MISE A JOUR
            try:
                scriptmaj = config.get( 'Version', 'SCRIPTMAJ' )
                xbmc.executescript( scriptmaj )

                #import MainGui
                #MainGui.show_main()
            except:
                logger.LOG( logger.LOG_DEBUG, "default : Exception pendant le chargement et/ou La mise a jour" )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
                dialog_error = True

        if dialog_error: xbmcgui.Dialog().ok( __language__( 111 ), __language__( 112 ) )
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
    DIALOG_PROGRESS.close()

def RUN_UNIT_TEST():
    try:
        # LOADING CONF
        print "Starting UNIT TESTS"
        import CONF
        config = CONF.ReadConfig()

        DIALOG_PROGRESS.update( -1, __language__( 101 ), __language__( 110 ) )
        if not config.getboolean( 'InstallPath', 'pathok' ):
            CONF.SetConfiguration()
        config = CONF.ReadConfig()
        del CONF

        # UNIT TEST
        
        # Write your unit tests Here
        # ...
        # ...
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        dialog_error = True
    DIALOG_PROGRESS.close()


if __name__ == "__main__":
    try:
        DIALOG_PROGRESS.create( __language__( 0 ), "", "" )
        if TEST_PERFORMANCE:
            import profile, pstats
            report_file = os.path.join( ROOTDIR, "MainPerform.profile.log" )
            profile.run( "MAIN()", report_file )
            pstats.Stats( report_file ).sort_stats( "time", "name" ).print_stats()
        elif UNIT_TEST:
            print "Running Unit tests"
            RUN_UNIT_TEST()      
            print "Tests done"      
        else:
            MAIN()
    except:
        #print_exc()
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        DIALOG_PROGRESS.close()