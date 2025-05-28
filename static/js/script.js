$(document).ready(function() {
    // Validation functions
    function verificarTelefone(telefone) {
        // Brazilian phone number format: (99) 99999-9999 or 99999999999
        const regex = /^(?:\(\d{2}\)\s)?(?:9\d{4}-\d{4}|\d{9,11})$/;
        return regex.test(telefone);
    }

    function verificarCPF(cpf) {
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


    // Add fade-out animation to messages
    document.addEventListener('DOMContentLoaded', function() {
        const messages = document.querySelectorAll('.popup');
        messages.forEach(message => {
            message.classList.add('fade-out');
            setTimeout(() => message.remove(), 300);
        });
    });

    // Helper functions
    function showPopup(message, isError) {
        const popup = $('<div>')
            .addClass('popup')
            .text(message);
        
        if (isError) {
            popup.addClass('error');
        } else {
            popup.addClass('success');
        }
        
        $('body').append(popup);
    }

    // Admin functionality
    if (window.location.pathname.includes('/admin/')) {
        // Helper functions for table editing
        function enableEditMode(row) {
            const cells = row.find('td:not(:last-child)');
            cells.each(function() {
                const cell = $(this);
                const text = cell.text();
                cell.html(`<input type="text" value="${text}" class="form-control">`);
            });

            const actionCell = row.find('td:last-child');
            actionCell.html(`
                <button class="save-btn btn btn-primary">Salvar</button>
                <span class="button-spacer"></span>
                <button class="cancel-btn btn btn-secondary">Cancelar</button>
            `);
        }

        function disableEditMode(row) {
            const cells = row.find('td:not(:last-child)');
            cells.each(function() {
                const cell = $(this);
                const input = cell.find('input');
                cell.text(input.val());
            });

            const actionCell = row.find('td:last-child');
            actionCell.html(`<button class="edit-btn btn btn-secondary">Editar</button>`);
        }

        // Search functionality
        $('#searchForm').on('submit', function(event) {
            event.preventDefault();
            const searchQuery = $('#search_query').val();
            const tableName = window.location.pathname.split('/').pop();

            if (!searchQuery) {
                showPopup('Por favor, preencha o campo de busca.', true);
                return;
            }

            $.ajax({
                url: '/admin/search',
                type: 'POST',
                data: {
                    table_name: tableName,
                    search_query: searchQuery
                },
                success: function(response) {
                    const tbody = $('#searchTable tbody');
                    tbody.empty();
                    
                    response.results.forEach(row => {
                        const tr = $('<tr>');
                        Object.values(row).forEach(value => {
                            tr.append($('<td>').text(value));
                        });
                        tr.append($('<td>').html('<button class="edit-btn btn btn-secondary">Editar</button>'));
                        tbody.append(tr);
                    });
                },
                error: function() {
                    showPopup('Erro ao buscar dados.', true);
                }
            });
        });

        // Clear search results when search query is cleared
        $('#search_query').on('input', function() {
            if (!this.value) {
                $('#searchTable tbody').empty();
            }
        });

        // Edit button functionality
        $(document).on('click', '.edit-btn', function() {
            const row = $(this).closest('tr');
            enableEditMode(row);
        });

        // Cancel edit
        $(document).on('click', '.cancel-btn', function() {
            const row = $(this).closest('tr');
            disableEditMode(row);
        });

        // Save edited data
        $(document).on('click', '.save-btn', function() {
            const row = $(this).closest('tr');
            const id = row.data('id');
            const tableName = window.location.pathname.split('/').pop();
            const updatedData = {};
            
            // Get column names from the table header
            const table = row.closest('table');
            const headers = table.find('thead th');
            
            // Collect the edited data
            row.find('td:not(:last-child)').each(function(index) {
                const columnName = headers.eq(index).text();
                const value = $(this).find('input').val();
                updatedData[columnName] = value;
            });

            // Send the updated data to the backend
            $.ajax({
                url: '/admin/update_data',
                type: 'POST',
                data: { id: id, table_name: tableName, ...updatedData },
                success: function(response) {
                    if (response.status === 'success') {
                        showPopup('Dados atualizados com sucesso!', false);
                        disableEditMode(row);
                    } else {
                        showPopup('Erro ao atualizar dados: ' + response.message, true);
                    }
                },
                error: function(error) {
                    showPopup('Erro ao atualizar dados. Tente novamente.', true);
                }
            });
        });
    }

    // Client functionality
    if (window.location.pathname.includes('/client/')) {
        // Consultation scheduling
        $('#scheduleForm').on('submit', function(event) {
            event.preventDefault();
            const formData = $(this).serialize();

            $.ajax({
                url: '/client/schedule',
                type: 'POST',
                data: formData,
                success: function(response) {
                    showPopup('Consulta agendada com sucesso!', false);
                    $(this).trigger('reset');
                },
                error: function() {
                    showPopup('Erro ao agendar consulta.', true);
                }
            });
        });

        // Delete consultation
        $(document).on('click', '.delete-btn', function() {
            const id = $(this).data('id');

            if (confirm('Tem certeza que deseja cancelar esta consulta?')) {
                $.ajax({
                    url: '/client/delete_consulta',
                    type: 'POST',
                    data: { id: id },
                    success: function(response) {
                        showPopup('Consulta cancelada com sucesso!', false);
                        $(this).closest('tr').remove();
                    },
                    error: function() {
                        showPopup('Erro ao cancelar consulta.', true);
                    }
                });
            }
        });
    }
});
