declare const Buffer: any;

export interface OutputItem {
  actPlanDate: string | null;
  closeReason: string | null;
  closeReasonComment: string | null;
  creationDate: string | null;
  creator: string | null;
  deal: string | null;
  dealCreationDate: string | null;
  dealId: string | null;
  dealIdentifier: string | null;
  dealLastUpdateDate: string | null;
  dealName: string | null;
  dealProduct: string | null;
  dealRevenueAmount: number | null;
  dealSource: string | null;
  dealStage: string | null;
  dealStageFinal: boolean | null;
  dealStageTransitionDate: string | null;
  deliveryType: string | null;
  description: string | null;
  directSupply: boolean | null;
  distributor: string | null;
  finalLicenseAmount: number | null;
  finalServiceAmount: number | null;
  finalServiceAmountByRevenueWithVAT: number | null;
  finalServiceAmountWithVAT: number | null;
  forecast: string | null;
  identifierRevenue: string | null;
  invoiceAmount: number | null;
  invoiceAmountWithVAT: number | null;
  lastUpdateDate: string | null;
  marketingEvent: string | null;
  organization: string | null;
  partner: string | null;
  product: string | null;
  quantity: number | null;
  responsiblePerson: string | null;
  revenue: number | null;
  siteLead: boolean | null;
  stageTransitionTime: string | null;
  totalProductAmount: number | null;
  unitOfMeasure: string | null;
}

function splitCsvRecords(text: string): string[] {
  const records: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const nextChar = text[i + 1];

    if (char === '"') {
      current += char;
      if (inQuotes && nextChar === '"') {
        current += nextChar;
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && nextChar === '\n') {
        i += 1;
      }
      if (current.trim().length > 0) {
        records.push(current);
      }
      current = '';
      continue;
    }

    current += char;
  }

  if (current.trim().length > 0) {
    records.push(current);
  }

  return records;
}

function parseCsvLine(line: string, delimiter: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    const nextChar = line[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === delimiter && !inQuotes) {
      result.push(current);
      current = '';
      continue;
    }

    current += char;
  }

  result.push(current);
  return result.map((item) => item.trim());
}

function detectDelimiter(records: string[]): string {
  const sample = records.slice(0, 5).join('\n');
  const candidates = [';', ',', '\t', '|'];
  let best = ',';
  let bestCount = -1;

  for (const candidate of candidates) {
    const count = sample.split(candidate).length - 1;
    if (count > bestCount) {
      best = candidate;
      bestCount = count;
    }
  }

  return best;
}

function toNullableString(value: unknown): string | null {
  if (value === undefined || value === null) return null;
  const text = String(value).trim();
  return text === '' ? null : text;
}

function toNumber(value: unknown): number | null {
  const text = toNullableString(value);
  if (text === null) return null;
  const normalized = text.replace(/\s+/g, '').replace(',', '.');
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function toBoolean(value: unknown): boolean | null {
  const text = toNullableString(value);
  if (text === null) return null;
  const normalized = text.toLowerCase();
  if (['true', '1', 'yes', 'да', 'y', 'x', 'final', 'done'].includes(normalized)) return true;
  if (['false', '0', 'no', 'нет', 'n'].includes(normalized)) return false;
  return null;
}

function extractPairNumber(value: unknown, index: number): number | null {
  const text = toNullableString(value);
  if (text === null) return null;
  const match = text.match(/(\d+)\s*[-:]\s*(\d+)/);
  if (!match) return null;
  return toNumber(match[index + 1]);
}

export default function(base64file: string): OutputItem[] {
  const text = Buffer.from(base64file, 'base64').toString('utf8');
  const records = splitCsvRecords(text);

  if (records.length === 0) return [];

  const delimiter = detectDelimiter(records);
  const headers = parseCsvLine(records[0], delimiter);

  return records.slice(1).map((line) => {
    const values = parseCsvLine(line, delimiter);
    const row: Record<string, string | null> = {};

    headers.forEach((header, index) => {
      row[header] = index < values.length ? values[index] : null;
    });

    const item: OutputItem = {
      actPlanDate: null,
      closeReason: null,
      closeReasonComment: null,
      creationDate: null,
      creator: null,
      deal: null,
      dealCreationDate: null,
      dealId: null,
      dealIdentifier: null,
      dealLastUpdateDate: null,
      dealName: null,
      dealProduct: null,
      dealRevenueAmount: null,
      dealSource: null,
      dealStage: null,
      dealStageFinal: null,
      dealStageTransitionDate: null,
      deliveryType: null,
      description: null,
      directSupply: null,
      distributor: null,
      finalLicenseAmount: null,
      finalServiceAmount: null,
      finalServiceAmountByRevenueWithVAT: null,
      finalServiceAmountWithVAT: null,
      forecast: null,
      identifierRevenue: null,
      invoiceAmount: null,
      invoiceAmountWithVAT: null,
      lastUpdateDate: null,
      marketingEvent: null,
      organization: null,
      partner: null,
      product: null,
      quantity: null,
      responsiblePerson: null,
      revenue: null,
      siteLead: null,
      stageTransitionTime: null,
      totalProductAmount: null,
      unitOfMeasure: null,
    };

    return item;
  });
}
