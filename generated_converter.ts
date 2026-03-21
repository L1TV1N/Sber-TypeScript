export interface OutputItem {
  passenger_id: string;
  pclass: string;
  name: string;
  sex: string;
  age?: number | null;
  sibsp: number;
  parch: number;
  ticket: string;
  fare: number;
  cabin: string;
  embarked: string;
  boat: string;
  body: string;
  home_dest: string;
  survived: number;
}

export default function(base64file: string): OutputItem[] {
  const decoded = Buffer.from(base64file, 'base64').toString('utf8');

  const lines = decoded.split(/\r?\n/)
    .filter(row => row.trim() !== '');

  if (!lines.length) return [];

  const headers = lines[0].split(',');

  // Helper for parsing CSV line with support of quotes and escaped quotes
  const parseCsvLine = (line: string): string[] => {
    let result: string[] = [];
    let inQuote = false;
    let currentField = '';
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        if (inQuote && line[i + 1] === '"') { // Escaped quote
          currentField += '"';
          i++;
        } else {
          inQuote = !inQuote;
        }
      } else if (char === ',' && !inQuote) {
        result.push(currentField);
        currentField = '';
      } else {
        currentField += char;
      }
    }
    result.push(currentField); // Add last field
    return result;
  };

  const rows = lines.slice(1).map(parseCsvLine);

  return rows.map((row, index) => {
    const mappedRow: OutputItem = {};
    headers.forEach(header => {
      const value = row[headers.indexOf(header)];
      switch (header) {
        case 'age':
          mappedRow.age = toNumber(value);
          break;
        case 'sibsp':
        case 'parch':
          mappedRow[header] = Number(value);
          break;
        case 'fare':
        case 'fare':
        case 'final_service_amount':
        case 'final_license_amount':
        case 'final_service_amount_by_revenue_with_vat':
        case 'final_service_amount_with_vat':
        case 'invoice_amount':
        case 'invoice_amount_with_vat':
        case 'revenue':
        case 'total_product_amount':
          mappedRow[header] = toNumber(value);
          break;
        case 'survived':
          mappedRow[header] = Number(value);
          break;
        default:
          mappedRow[header] = value || null;
      }
    });
    return mappedRow;
  });
}

function toNumber(value: string | null): number | null {
  if (value == null) return null;
  const parsed = parseFloat(value);
  return isNaN(parsed) ? null : parsed;
}