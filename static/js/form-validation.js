// Form validation functions
document.addEventListener('DOMContentLoaded', function() {
    // CPF validation function
    function validarCPF(cpf) {
        // Remove any non-digit characters
        cpf = cpf.replace(/\D/g, '');
        
        // Check if CPF has 11 digits
        if (cpf.length !== 11) return false;
        
        // Check if all digits are the same
        if (/^\d+?(?=\d+$)\d{11}$/.test(cpf)) return false;
        
        // Calculate first check digit
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let firstDigit = (sum % 11 < 2) ? 0 : 11 - (sum % 11);
        
        // Calculate second check digit
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        let secondDigit = (sum % 11 < 2) ? 0 : 11 - (sum % 11);
        
        // Check if calculated digits match
        return (firstDigit === parseInt(cpf.charAt(9))) && (secondDigit === parseInt(cpf.charAt(10)));
    }

    // Phone number validation function
    function validarTelefone(telefone) {
        // Accepts formats:
        // - (99) 99999-9999
        // - 99999999999
        // - 99 999999999
        // - 99 99999-9999
        const regex = /^(?:\(\d{2}\)\s?|\d{2}\s?)(?:9\d{4}[-\s]?\d{4}|\d{4}[-\s]?\d{4})$/;
        return regex.test(telefone);
    }

    // Format CPF input
    function formatarCPF(cpf) {
        // Remove non-digit characters and limit to 11 digits
        cpf = cpf.replace(/\D/g, '').substring(0, 11);
        
        // Apply formatting only if we have digits
        if (cpf.length > 0) {
            cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
            if (cpf.length > 3) {
                cpf = cpf.replace(/(\d{3})\.(\d{3})(\d)/, '$1.$2.$3');
                if (cpf.length > 7) {
                    cpf = cpf.replace(/(\d{3})\.(\d{3})\.(\d{3})(\d)/, '$1.$2.$3-$4');
                }
            }
            // Remove any extra formatting that might have been added
            cpf = cpf.substring(0, 14); // Max length: 999.999.999-99
        }
        return cpf;
    }

    // Format phone number input
    function formatarTelefone(telefone) {
        // Remove all non-digit characters
        const digits = telefone.replace(/\D/g, '');
        
        // Format based on length
        if (digits.length <= 2) {
            return digits;
        } else if (digits.length <= 10) {
            // Format as XX XXXX-XXXX or XX XXXXX-XXXX
            const ddd = digits.substring(0, 2);
            const firstPart = digits.substring(2, 6);
            const secondPart = digits.substring(6);
            
            if (secondPart) {
                return `${ddd} ${firstPart}${secondPart ? '-' + secondPart : ''}`;
            }
            return `${ddd} ${firstPart}`;
        } else {
            // Format as (XX) 9XXXX-XXXX
            const ddd = digits.substring(0, 2);
            const firstPart = digits.substring(2, 7);
            const secondPart = digits.substring(7, 11);
            return `(${ddd}) ${firstPart}${secondPart ? '-' + secondPart : ''}`;
        }
    }

    // Add validation to register form
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        const cpfInput = registerForm.querySelector('input[name="id"]');
        const phoneInput = registerForm.querySelector('input[name="phone"]');
        
        if (cpfInput) {
            // Format CPF on input
            cpfInput.addEventListener('input', function(e) {
                // Store cursor position
                const start = this.selectionStart;
                const end = this.selectionEnd;
                
                // Format the value
                this.value = formatarCPF(this.value);
                
                // Restore cursor position (adjust for added formatting characters)
                const diff = this.value.length - (end - start);
                this.setSelectionRange(start + diff, start + diff);
            });
            
            // Prevent typing more than 11 digits
            cpfInput.addEventListener('keypress', function(e) {
                const currentValue = this.value.replace(/\D/g, '');
                if (currentValue.length >= 11 && e.key !== 'Backspace' && e.key !== 'Delete' && 
                    !e.ctrlKey && !e.metaKey && e.key.length === 1) {
                    e.preventDefault();
                }
            });
            
            // Validate CPF on form submission
            registerForm.addEventListener('submit', function(e) {
                const cpf = cpfInput.value.replace(/\D/g, '');
                if (!validarCPF(cpf)) {
                    e.preventDefault();
                    alert('Por favor, insira um CPF válido.');
                    cpfInput.focus();
                    return false;
                }
                
                if (phoneInput && !validarTelefone(phoneInput.value)) {
                    e.preventDefault();
                    alert('Por favor, insira um telefone válido. Formato: (99) 99999-9999');
                    phoneInput.focus();
                    return false;
                }
                
                return true;
            });
        }
        
        if (phoneInput) {
            // Format phone number on input
            phoneInput.addEventListener('input', function(e) {
                this.value = formatarTelefone(this.value);
            });
        }
    }
    
    // Add validation to login form
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        const identifierInput = loginForm.querySelector('input[name="identifier"]');
        
        loginForm.addEventListener('submit', function(e) {
            const identifier = identifierInput.value.trim();
            
            // Check if identifier is a CPF (contains only numbers and is 11 digits)
            if (/^\d{11}$/.test(identifier) || /^\d{3}\.\d{3}\.\d{3}-\d{2}$/.test(identifier)) {
                const cpf = identifier.replace(/\D/g, '');
                if (!validarCPF(cpf)) {
                    e.preventDefault();
                    alert('Por favor, insira um CPF válido.');
                    identifierInput.focus();
                    return false;
                }
            }
            
            return true;
        });
    }
});
