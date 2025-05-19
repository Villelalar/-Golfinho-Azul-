$(document).ready(function() {
    // Function to get user role
    function getUserRole() {
        const path = window.location.pathname;
        if (path.includes('/admin/')) {
            return 'admin';
        }
        if (path.includes('/client/')) {
            return 'client';
        }
        return 'admin';
    }

    // Function to show popups
    function showPopup(message, isError) {
        const popup = $('<div>').addClass('popup').text(message);
        if (isError) {
            popup.addClass('error');
        } else {
            popup.addClass('success');
        }
        $('body').append(popup);
        setTimeout(() => {
            popup.css('opacity', '0');
            setTimeout(() => popup.remove(), 500);
        }, 2000);
    }

    // Function to get table name from URL
    function getTableNameFromURL() {
        const path = window.location.pathname;
        const parts = path.split('/');
        return parts[parts.length - 1];
    }

    // Function to validate Brazilian phone format
    function isValidBrazilianPhone(phone) {
        const regex = /^(?:\+55)?\s?(?:\(?\d{2}\)?)?\s?9?\d{4}-?\d{4}$/;
        return regex.test(phone);
    }

    // Admin functionality
    if (getUserRole() === 'admin') {
        // Collect table data for validation
        let existingIds = [];
        let existingNames = [];
        let existingEmails = [];
        let existingPhones = [];

        $('.users-table tbody tr').each(function() {
            existingIds.push($(this).find('td:eq(0)').text().trim());
            existingNames.push($(this).find('td:eq(1)').text().trim());
            existingEmails.push($(this).find('td:eq(2)').text().trim());
            existingPhones.push($(this).find('td:eq(3)').text().trim());
        });

        // Search functionality
        $('#searchForm').on('submit', function(event) {
            event.preventDefault();
            const searchQuery = $('#search_query').val();
            const tableName = getTableNameFromURL();

            if (!searchQuery) {
                showPopup('Por favor, preencha o campo de busca.', true);
                return;
            }

            console.log("Searching in table:", tableName);
            console.log("Search query:", searchQuery);

            $.ajax({
                url: '/admin/search',
                type: 'POST',
                data: {
                    table_name: tableName,
                    search_query: searchQuery
                },
                dataType: 'text',
                success: function(responseText) {
                    const response = JSON.parse(responseText);
                    if (response.status === 'error') {
                        showPopup(response.message, true);
                        return;
                    }

                    const tbody = $('#searchTable tbody');
                    tbody.empty();
                    // Get column headers from the table
                    const headers = $('#searchTable thead th').map(function() {
                        return $(this).text();
                    }).get();
                    
                    response.results.forEach(row => {
                        const tr = $('<tr>');
                        headers.forEach(header => {
                            const cellValue = row[header];
                            if (cellValue !== undefined) {
                                if (cellValue === null) {
                                    tr.append($('<td>').text('Não Atribuído'));
                                } else {
                                    // Check if the value is an ISO string and convert it to MySQL format
                                    if (typeof cellValue === 'string' && cellValue.includes('T')) {
                                        const isoDate = new Date(cellValue);
                                        const mysqlFormat = isoDate.getFullYear() + '-' + 
                                            String(isoDate.getMonth() + 1).padStart(2, '0') + '-' +
                                            String(isoDate.getDate()).padStart(2, '0') + ' ' +
                                            String(isoDate.getHours()).padStart(2, '0') + ':' +
                                            String(isoDate.getMinutes()).padStart(2, '0') + ':' +
                                            String(isoDate.getSeconds()).padStart(2, '0');
                                        tr.append($('<td>').text(mysqlFormat));
                                    } else {
                                        tr.append($('<td>').text(cellValue));
                                    }
                                }
                            }
                        });
                        tr.append($('<td>').append($('<button>').addClass('edit-btn').text('Editar')));
                        tbody.append(tr);
                    });
                    $('#searchResults').show();
                },
                error: function(xhr, status, error) {
                    console.error("Search error:", error);
                    showPopup("Erro ao realizar busca.", true);
                }
            });
        });

        // Clear search results when search query is cleared
        $('#search_query').on('input', function() {
            if (!this.value) {
                $('#searchResults').hide();
            }
        });

        // Add data functionality
        $('#addDataForm').on('submit', function(event) {
            event.preventDefault();
            const tableName = getTableNameFromURL();
            const formData = $(this).serializeArray();
            const newData = {};
            const userRole = getUserRole();

            // Skip ID fields
            formData.forEach(field => {
                if (!field.name.toLowerCase().includes('id')) {
                    newData[field.name] = field.value;
                }
            });

            $.ajax({
                url: `/${userRole}/add_data`,
                type: 'POST',
                data: { ...newData, table_name: tableName },
                success: function(response) {
                    if (response.status === 'error') {
                        showPopup(response.message, true);
                    } else {
                        showPopup('Dados adicionados com sucesso!', false);
                        // Refresh the table
                        location.reload();
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Add data error:", error);
                    showPopup("Erro ao adicionar dados.", true);
                }
            });
        });

        // Edit button functionality
        $(document).on('click', '.edit-btn', function() {
            const row = $(this).closest('tr');
            const cells = row.find('td:not(:last-child)');
            cells.each(function() {
                const cell = $(this);
                const text = cell.text();
                cell.html(`<input type="text" value="${text}" name="${cell.index()}">`);
            });

            const actionCell = row.find('td:last-child');
            actionCell.html(`
                <button class="save-btn">Salvar</button>
                <span class="button-spacer"></span>
                <button class="cancel-btn">Cancelar</button>
            `);
        });

        // Cancel edit
        $(document).on('click', '.cancel-btn', function() {
            const row = $(this).closest('tr');
            const cells = row.find('td:not(:last-child)');
            cells.each(function() {
                const cell = $(this);
                const text = cell.find('input').val();
                cell.text(text);
            });

            const actionCell = row.find('td:last-child');
            actionCell.html('<button class="edit-btn">Editar</button>');
        });

        // Evento de clique no botão "Salvar"
        $(document).on('click', '.save-btn', function() {
            const row = $(this).closest('tr');
            const id = row.data('id');
            const tableName = getTableNameFromURL();
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
                contentType: 'application/json',
                data: JSON.stringify({ id: id, table_name: tableName, ...updatedData }),
                success: function(response) {
                    if (response.status === 'success') {
                        showPopup('Dados atualizados com sucesso!', false);
                        disableEditMode(row);
                    } else {
                        showPopup('Erro ao atualizar dados: ' + response.message, true);
                    }
                },
                error: function(error) {
                    console.error('Erro ao atualizar dados:', error);
                    showPopup('Erro ao atualizar dados. Tente novamente.', true);
                }
            });
        });
    }

    // Client functionality
    if (getUserRole() === 'client') {
        // Edit appointment
        $(document).on('click', '.edit-btn', function() {
            const row = $(this).closest('tr');
            const cells = row.find('td:not(:last-child)');
            cells.each(function() {
                const cell = $(this);
                const text = cell.text();
                cell.html(`<input type="text" value="${text}">`);
            });

            const actionCell = row.find('td:last-child');
            actionCell.html(`
                <button class="save-btn">Salvar</button>
                <span class="button-spacer"></span>
                <button class="cancel-btn">Cancelar</button>
            `);
        });

        // Cancel edit
        $(document).on('click', '.cancel-btn', function() {
            const row = $(this).closest('tr');
            const cells = row.find('td:not(:last-child)');
            cells.each(function() {
                const cell = $(this);
                const input = cell.find('input');
                cell.text(input.val());
            });

            const actionCell = row.find('td:last-child');
            actionCell.html(`<button class="edit-btn">Editar</button>`);
        });

        // Save edited appointment
        $(document).on('click', '.save-btn', function() {
            const row = $(this).closest('tr');
            const id = row.data('id');
            const data = row.find('td:eq(0) input').val();
            const hora = row.find('td:eq(1) input').val();
            const status = row.find('td:eq(2) input').val();
            const detalhes = row.find('td:eq(3) input').val();

            $.ajax({
                url: '/client/consulta/atualizarconsulta',
                type: 'POST',
                data: {
                    consulta_id: id,
                    data: data,
                    hora: hora,
                    status: status,
                    detalhes: detalhes
                },
                success: function(response) {
                    if (response.status === 'success') {
                        location.reload();
                    } else {
                        alert('Erro ao atualizar consulta: ' + response.error);
                    }
                },
                error: function() {
                    alert('Erro ao atualizar consulta. Tente novamente.');
                }
            });
        });

        // Delete appointment
        $(document).on('click', '.delete-btn', function() {
            if (!confirm('Tem certeza que deseja excluir esta consulta?')) {
                return;
            }

            const row = $(this).closest('tr');
            const id = row.data('id');

            $.ajax({
                url: '/client/consulta/deletarconsulta',
                type: 'POST',
                data: { consulta_id: id },
                success: function(response) {
                    if (response.status === 'success') {
                        row.remove();
                    } else {
                        alert('Erro ao excluir consulta: ' + response.error);
                    }
                },
                error: function() {
                    alert('Erro ao excluir consulta. Tente novamente.');
                }
            });
        });

        // Search appointments
        $('#searchForm').on('submit', function(event) {
            event.preventDefault();
            const query = $('#search_query').val();
            
            if (!query) {
                alert('Por favor, preencha o campo de busca.');
                return;
            }

            $.ajax({
                url: '/client/consulta/search',
                type: 'POST',
                data: { query: query },
                success: function(response) {
                    if (response.error) {
                        alert(response.error);
                        return;
                    }

                    const tableBody = $('#appointmentsTable tbody');
                    tableBody.empty();

                    response.results.forEach(consulta => {
                        const tr = $('<tr>').data('id', consulta.id);
                        tr.append(
                            $('<td>').text(consulta.data),
                            $('<td>').text(consulta.hora),
                            $('<td>').text(consulta.status),
                            $('<td>').text(consulta.detalhes),
                            $('<td>').html('<button class="edit-btn">Editar</button> <button class="delete-btn">Excluir</button>')
                        );
                        tableBody.append(tr);
                    });
                },
                error: function() {
                    alert('Erro ao buscar consultas. Tente novamente.');
                }
            });
        });
    }

    // Helper functions for table editing
    function enableEditMode(row) {
        const cells = row.find('td:not(:last-child)');
        cells.each(function() {
            const cell = $(this);
            const text = cell.text();
            cell.html(`<input type="text" value="${text}">`);
        });

        const actionCell = row.find('td:last-child');
        actionCell.html(`
            <button class="save-btn">Salvar</button>
            <button class="cancel-btn">Cancelar</button>
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
        actionCell.html(`<button class="edit-btn">Editar</button>`);
    }
});
