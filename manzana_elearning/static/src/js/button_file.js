/** @odoo-module **//** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { session } from "@web/session";

publicWidget.registry.FileUploadWidget = publicWidget.Widget.extend({
        selector: '.file-upload-container',
        events: {
            'click .file-upload-icon': '_onClickUpload',
            'change input[type="file"]': '_onFileSelected',
        },

        start: function () {
            this.assignmentId = this.$el.data('assignment-id');
            console.log(session.user_id)
            console.log(this.assignmentId)
            return this._super.apply(this, arguments);
        },

        _onClickUpload: function (ev) {
            ev.preventDefault();
            console.log('aqui')
            this.$('input[type="file"]').click();
        },

        _onFileSelected: function (ev) {
            var file = ev.target.files[0];
            console.log(file)
            if (file) {
                this.$('.upload-text').hide();
                this.$('.file-name-display').text(file.name);
                this._uploadFile(file);
            }
        },

        _uploadFile: function (file) {
            var self = this;
            var formData = new FormData();
            formData.append('assignment_id', this.assignmentId);
            formData.append('submitted_file', file);

            $.ajax({
                url: '/submit/assignment',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    // Manejar la respuesta exitosa
                    console.log('Archivo subido con éxito');
                    // Aquí puedes actualizar la UI o mostrar un mensaje de éxito
                },
                error: function (xhr, status, error) {
                    // Manejar el error
                    console.error('Error al subir el archivo:', error);
                    // Aquí puedes mostrar un mensaje de error al usuario
                }
            });
        },
    });

export default publicWidget.registry.FileUploadWidget;