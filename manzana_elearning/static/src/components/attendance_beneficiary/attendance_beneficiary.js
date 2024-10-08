/** @odoo-module */

import { registry } from "@web/core/registry";

import { useService } from "@web/core/utils/hooks";

import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { CheckBox } from "@web/core/checkbox/checkbox";

import { Component, useState, onMounted } from "@odoo/owl";



export class AttendanceBeneficiary extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            slideChanel : this.env.model.root.evalContext.id,
            beneficiarys : [],
            date: luxon.DateTime.now(),
            today: luxon.DateTime.now(),
        });

        onMounted(async ()=>{
            const { slideChanel } = this.state;
            let attendees = await this._showAttendees(slideChanel);
            this.state.beneficiarys = attendees?.course_attendees
            console.log(attendees)
        })
    }

    async _showAttendees(slideChanel) {
        
        try {
            const configs = await this.rpc("/manzana_beneficiary/attendees", {
                slideChanel: slideChanel
            });
            return JSON.parse(configs)
        } catch (error) {
            console.error("Error en la llamada RPC:", error);
        }
    }

    handleClick() {
        console.log('Clic en el componente de Asistencias');
    }

    onDateChanged(ev) {
        const date = ev.toFormat('dd/MM/yyyy');
    }

    onOptionChanged(value) {
        console.log(value)
    }
}

AttendanceBeneficiary.template = "manzana_elearning.attendance_beneficiary";
AttendanceBeneficiary.components = { DatePicker: DateTimePicker, DateTimeInput, CheckBox };

export const attendanceBeneficiary = {
    component: AttendanceBeneficiary
};
registry.category("view_widgets").add("mze_attendance_beneficiary", attendanceBeneficiary);