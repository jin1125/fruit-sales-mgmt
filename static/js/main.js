'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const inputCsvFile = document.getElementById('id_csv');

  inputCsvFile.addEventListener('change', () => {
    const displayCsvFilename = document.getElementById(
      'sales-csv-form-filename'
    );
    const choseCsvFilename = inputCsvFile.files[0].name;

    displayCsvFilename.textContent = choseCsvFilename
  });
});
