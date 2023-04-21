import QtQuick
import LKWidgets

LKWindow {
    title: 'Markdown Image Paste'
    width: 480
    height: 108

    LKColumn {
        anchors {
            fill: parent
            margins: 12
        }
        alignment: 'left'
        
        component MyInput: LKInput {
            width: parent.width
            textColor: isValidPath ? 'black' : 'red'
            property bool isValidPath: false
        }
        
        MyInput {
            id: _doc_path
            width: parent.width
            textHint: 'Input a dirpath to your document'
            onTextChanged: {
                this.isValidPath = py.main.set_doc_root(this.text)
            }
        }
        
        MyInput {
            id: _img_path
            textHint: 'Input a dirpath to save images'
            onTextChanged: {
                this.isValidPath = py.main.set_img_root(this.text)
            }
        }

        LKText {
            id: _mdtext
            text: '<font color="grey">Click below button to dump image from ' +
                  'clipboard to local.</font>'
        }

        LKButton {
            anchors.horizontalCenter: parent.horizontalCenter
            text: 'Dump image'
            onClicked: {
                const link = py.main.dump_image()
                _mdtext.text = link
            }
        }
    }
}
