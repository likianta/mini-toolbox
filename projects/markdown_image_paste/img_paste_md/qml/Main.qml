import QtQuick
import LKWidgets

LKWindow {
    title: 'Markdown Image Paste'
    width: 480
    height: 88

    LKColumn {
        anchors {
            fill: parent
            margins: 12
        }
        alignment: 'left'

        LKInput {
            id: _assets_dir
            width: parent.width
            textColor: is_valid_path ? 'black' : 'red'
            textHint: 'Input a dirpath to save images'

            property bool is_valid_path: false

            onTextChanged: {
                this.is_valid_path = pymain.update_assets_dirpath(this.text)
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
                const link = pymain.dump_image()
                _mdtext.text = link
            }
        }
    }
}
