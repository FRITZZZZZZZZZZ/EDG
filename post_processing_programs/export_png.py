import os
import sys

def export_csv(argument_vector):
    try:
        jobname = argument_vector[1]
    except:
        pass
    

    current_working_directory = os.getcwd()
    print(current_working_directory)
    print(jobname, "DAS IST DER JOBNMAME")

    with open("SessionFileShowAndExportPost.ofs", 'w') as session_file_export:
        session_file_export.write(
            f"""
            mode(Post)
            file.open.apply("{current_working_directory}/{jobname}.erg/header.bin", format="OFSolv/Results", variables=Recommended, increments=All, curves=OnDemand)
            showMin()
            showMax()
            view.multiView.setActive(views=nextView)
            setVariable("Scalar:Formability", view="3D View 2")
            flcCreateKeeler(materialName="Keeler 1", thickness="0.8", n="0.2", r=1)
            flcRemoveItem(item="process(1):Blank")
            flcAddItem(flc="Keeler 1", item="process(1):Blank")
            setOption("Snapshot/Background Color Type", value="User Defined")
            takeSnapshot("3D View", filename="{current_working_directory}/{jobname}.png", backgroundColor=black, drawTitle=On, drawLogo=On, drawCoordSys=On, drawScale=On, drawLabel=On, drawBorder=Off)
            quit()
            """)
    
    try:
        os.system(f"ofd -s SessionFileShowAndExportPost.ofs -b")
    except:
        print("Export did not work.")

instruction = sys.argv
export_csv(instruction)