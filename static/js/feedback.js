function People (feedback, name, surname, email, phone) {
    
    this.feedback = feedback;
    this.name = name;
    this.surname = surname;
    this.email = email;
    this.phone = phone;

    this.sayHi = () => {
        return ('Здравствуйте, ' + this.name + ' ' + this.surname + 
        '. Ваш почтовый адрес: ' + this.email + 
        '. Ваш номер телефона: ' + this.phone + 
        '. Мы вам перезвоним.')
    };
}

var send_feedback = new Vue ({
    el: '#send_feedback',
    data: {
        feedback: '',
        name: '',
        surname: '',
        email: '',
        phone: '',
        feedback_button_blocker: true,
        phone_blocker: false,
        show_one: false,
        show_two: false,
        show_three: false,
        show_Jesus: false,
        show_enough: false,
        end_game: false,
        number: 80000000000,
    },
    methods: {
        send_feedback_button: function () {
            const man = new People(this.feedback, this.name, this.surname, this.email, this.phone);
            alert(man.sayHi());
            this.feedback_button_blocker = true;
            this.feedback = this.name = this. surname = this.email = this.phone = ''
        },

        unlock_button: function () {
            if (this.feedback.length != 0 && this.name.length != 0 && this.surname.length != 0 && this.email.length != 0 && this.phone.length == 11) {
                this.feedback_button_blocker = false;
            } else {
                this.feedback_button_blocker = true;
            }
        },

        choose_var_one: function() {
            this.phone = '80000000000'
            this.show_one = true;
            this.show_two = this.show_three = this.show_Jesus = false;
            this.phone_blocker = true;     
        },
        
        choose_var_two: function() {
            this.phone = '80000000000'
            this.show_two = true;
            this.show_one = this.show_three = this.show_Jesus = false;
            this.phone_blocker = true;
        },

        choose_var_three: function() {
            this.phone = '80000000000'
            this.show_three = true;  
            this.show_two = this.show_one = this.show_Jesus = false;
            this.phone_blocker = true;
        },

        choose_var_Jesus: function () {
            this.phone = '8';
            this.show_Jesus = true;
        },

        do_number_to_phone: function() {
            this.phone = String(this.number);
        },

        randomize_number: function() {
            this.phone = String(Math.round(Math.random() * (89999999999 - 80000000000) + 89999999999) - 10000000000);
        },

        sum_one_number: function() {
            if (this.phone == '') {
                this.phone = '80000000000'
            }
            this.phone = Number(this.phone)
            this.phone += 1;
            this.phone = String(this.phone)
        },

        delete_last_string_element: function(str) {
            if (str.length != 1) {
                return str.substring(0, str.length - 1);
            } else {
                return str;
            }
            
        },
    },
    delimiters: ['[[',']]']
})
