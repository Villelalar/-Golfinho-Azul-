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
            setTimeout(() => {
                message.classList.add('fade-out');
                setTimeout(() => message.remove(), 700); // 700ms igual ao CSS
            }, 2000); // Mostra por 2 segundos antes de sumir
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
        
        setTimeout(() => {
            popup.addClass('fade-out');
            setTimeout(() => popup.remove(), 700); 
        }, 3000);
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
                <button class="save-btn btn btn-success"><i class="fas fa-save"></i></button>
                <span class="button-spacer"></span>
                <button class="cancel-btn btn btn-warning"><i class="fas fa-times"></i></button>
                <span class="button-spacer"></span>
                <button class="delete-btn btn btn-danger"><i class="fas fa-trash-alt"></i></button>
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

                    // Exibe a div de resultados
                    $('#searchResults').show();

                    response.results.forEach(row => {
                        const tr = $('<tr>');
                        // Pega a ordem dos cabeçalhos (exceto "Ações" e "password_hash")
                        const headers = $('#searchTable thead th').map(function() {
                            return $(this).text();
                        }).get().filter(h => h !== 'Ações' && h !== 'password_hash');
                        headers.forEach(key => {
                            tr.append($('<td>').text(row[key] !== undefined ? row[key] : ''));
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
                $('#searchResults').hide();
                showPopup('Pesquisa limpa', false);
            }
        });
        
       
        $('#searchForm').append('<button type="button" id="clearSearch" class="btn btn-danger">Limpar</button>');
        $('#clearSearch').on('click', function() {
            $('#search_query').val('');
            $('#searchTable tbody').empty();
            $('#searchResults').hide();
            showPopup('Pesquisa limpa', false);
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

        // Delete row functionality
        let currentRowToDelete = null;
        let currentTableName = '';
        
        // Show delete confirmation modal
        function showDeleteConfirmation(row, tableName) {
            currentRowToDelete = row;
            currentTableName = tableName;
            $('#deleteConfirmationModal').fadeIn(200);
        }
        
        // Handle delete confirmation
        $('#confirmDeleteBtn').on('click', function() {
            if (!currentRowToDelete) return;
            
            const id = currentRowToDelete.data('id');
            if (!id) {
                console.error('ID not found for the row');
                showPopup('Erro: Não foi possível identificar o registro para exclusão', true);
                $('#deleteConfirmationModal').fadeOut(200);
                return;
            }
            
            $.ajax({
                url: '/admin/delete_data',
                type: 'POST',
                data: { 
                    table_name: currentTableName,
                    id: id
                },
                success: function(response) {
                    if (response.status === 'success') {
                        showPopup('Registro excluído com sucesso!', false);
                        currentRowToDelete.fadeOut(400, function() {
                            currentRowToDelete.remove();
                        });
                    } else {
                        showPopup('Erro ao excluir registro: ' + (response.message || 'Erro desconhecido'), true);
                    }
                },
                error: function(xhr) {
                    try {
                        const response = xhr.responseJSON || {};
                        showPopup('Erro: ' + (response.error || 'Erro ao processar a requisição'), true);
                    } catch (e) {
                        showPopup('Erro ao processar a resposta do servidor', true);
                    }
                },
                complete: function() {
                    $('#deleteConfirmationModal').fadeOut(200);
                    currentRowToDelete = null;
                    currentTableName = '';
                }
            });
        });
        
        // Handle cancel button
        $('#cancelDeleteBtn').on('click', function() {
            $('#deleteConfirmationModal').fadeOut(200);
            currentRowToDelete = null;
            currentTableName = '';
        });
        
        // Close modal when clicking outside
        $(document).on('click', '#deleteConfirmationModal', function(e) {
            if (e.target === this) {
                $(this).fadeOut(200);
                currentRowToDelete = null;
                currentTableName = '';
            }
        });
        
        // Handle delete button click
        $(document).on('click', '.delete-btn', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const row = $(this).closest('tr');
            const id = row.data('id');
            const tableName = window.location.pathname.split('/').pop();
            
            if (!id) {
                console.error('ID not found for the row');
                showPopup('Erro: Não foi possível identificar o registro para exclusão', true);
                return;
            }
            
            showDeleteConfirmation(row, tableName);
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
                let value = $(this).find('input').val();

                // Só converte se for campo de data/hora
                if (columnName.toLowerCase().includes('data') || columnName.toLowerCase().includes('created_at') || columnName.toLowerCase().includes('datetime')) {
                    value = formatDatetimeLocalToSQL(value);
                }

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

    function formatDatetimeLocalToSQL(datetimeLocal) {
        // datetimeLocal: '2025-05-27T12:43' ou '2025-05-27T12:43:56'
        if (!datetimeLocal) return '';
        // Se já está no formato SQL, retorna direto
        if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?$/.test(datetimeLocal)) {
            return datetimeLocal.length === 16 ? datetimeLocal + ':00' : datetimeLocal;
        }
        // Se está no formato datetime-local, converte
        if (datetimeLocal.includes('T')) {
            let [date, time] = datetimeLocal.split('T');
            if (time.length === 5) time += ':00';
            return `${date} ${time}`;
        }
        return datetimeLocal;
    }


});
//fazer o dropdownContent aparecer e desaparecer ao clicar no botão de "meu perfil"
document.addEventListener('DOMContentLoaded', function() {
    const profileBtn = document.querySelector('.profileBtn');
    const dropdownContent = document.querySelector('.dropdownContent');
    if (profileBtn && dropdownContent) {
        // Alterna a visibilidade ao clicar no botão
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Evita propagação do clique
            dropdownContent.classList.toggle('show-profile-btn');
        });

        // Fecha o dropdown se clicar fora dele
        document.addEventListener('click', function(event) {
            if (
                !dropdownContent.contains(event.target) &&
                event.target !== profileBtn
            ) {
                dropdownContent.classList.remove('show-profile-btn');
            }
        });
    }
});
