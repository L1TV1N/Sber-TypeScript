export interface OutputItem {
  actPlanDate?: string;
  closeReason?: string;
  closeReasonComment?: string;
  creationDate?: string;
  creator?: string;
  deal?: string;
  dealCreationDate?: string;
  dealId?: string;
  dealIdentifier?: string;
  dealLastUpdateDate?: string;
  dealName?: string;
  dealProduct?: string;
  dealRevenueAmount?: number;
  dealSource?: string;
  dealStage?: string;
  dealStageFinal?: boolean;
  dealStageTransitionDate?: string;
  deliveryType?: string;
  description?: string;
  directSupply?: boolean;
  distributor?: string;
  finalLicenseAmount?: number;
  finalServiceAmount?: number;
  finalServiceAmountByRevenueWithVAT?: number;
  finalServiceAmountWithVAT?: number;
  forecast?: string;
  identifierRevenue?: string;
  invoiceAmount?: number;
  invoiceAmountWithVAT?: number;
  lastUpdateDate?: string;
  marketingEvent?: string;
  organization?: string;
  partner?: string;
  product?: string;
  quantity?: number;
  responsiblePerson?: string;
  revenue?: number;
  siteLead?: boolean;
  stageTransitionTime?: string;
  totalProductAmount?: number;
  unitOfMeasure?: string;
}

export default function(base64file: string): OutputItem[] {
  const decoded = Buffer.from(base64file, 'base64').toString('utf8');
  const rows = decoded.split(/\r?\n/).filter(row => row.trim() !== '');

  return rows.map(parseCsvLine)
    .map((row: any[]) => ({
      actPlanDate: toDate(row['Плановая дата акта']),
      closeReason: toNullIfEmpty(row['Сделка - Причина закрытия']),
      closeReasonComment: toNullIfEmpty(row['Сделка - Комментарий к причине закрытия']),
      creationDate: toDate(row['Дата создания']),
      creator: toNullIfEmpty(row['Создал']),
      deal: toNullIfEmpty(row['Сделка']),
      dealCreationDate: toDate(row['Сделка - Дата создания']),
      dealId: toNullIfEmpty(row['Сделка - ID сделки']),
      dealIdentifier: toNullIfEmpty(row['Сделка - Идентификатор']),
      dealLastUpdateDate: toDate(row['Сделка - Дата последнего обновления']),
      dealName: toNullIfEmpty(row['Сделка - Название']),
      dealProduct: toNullIfEmpty(row['Сделка - Продукт']),
      dealRevenueAmount: toNumber(row['Сделка - Сумма выручки']),
      dealSource: toNullIfEmpty(row['Источник сделки']),
      dealStage: toNullIfEmpty(row['Сделка - Стадия']),
      dealStageFinal: toBoolRu(row['Сделка - Стадия (Сделка)'] === 'Закрыта'),
      dealStageTransitionDate: toDate(row['Сделка - Дата перехода объекта на новую стадию']),
      deliveryType: toNullIfEmpty(row['Тип поставки']),
      description: toNullIfEmpty(row['Сделка - Описание']),
      directSupply: toBoolRu(row['Сделка - Прямая поставка'] === 'Да'),
      distributor: toNullIfEmpty(row['Сделка - Дистрибьютор']),
      finalLicenseAmount: toNumber(row['Сделка - Итоговая сумма лицензий']),
      finalServiceAmount: toNumber(row['Сделка - Итоговая сумма услуг']),
      finalServiceAmountByRevenueWithVAT: toNumber(row['Сделка - Итоговая сумма услуг по выручке (с НДС)']),
      finalServiceAmountWithVAT: toNumber(row['Сделка - Итоговая сумма услуг (с НДС)']),
      forecast: toNullIfEmpty(row['Сделка - Прогноз']),
      identifierRevenue: toNullIfEmpty(row['Идентификатор (Выручка)']),
      invoiceAmount: toNumber(row['Сделка - Сумма акта']),
      invoiceAmountWithVAT: toNumber(row['Сделка - Сумама акта (с НДС)']),
      lastUpdateDate: toDate(row['Сделка - Дата последнего обновления']),
      marketingEvent: toNullIfEmpty(row['Сделка - Маркетинговое мероприятие']),
      organization: toNullIfEmpty(row['Сделка - Организация']),
      partner: toNullIfEmpty(row['Сделка - Партнер по сделке']),
      product: toNullIfEmpty(row['Продукт']),
      quantity: toNumber(row['Количество']),
      responsiblePerson: toNullIfEmpty(row['Сделка - Ответственный']),
      revenue: toNumber(row['Выручка']),
      siteLead: toBoolRu(row['Сделка - Лид с сайта'] === 'Да'),
      stageTransitionTime: toDate(row['Сделка - Дата перехода объекта на новую стадию']),
      totalProductAmount: toNumber(row['Сделка - Итоговая сумма продуктов']),
      unitOfMeasure: toNullIfEmpty(row['Единица измерения'])
    }));
}

function parseCsvLine(line: string): string[] {
  const parts = line.split('"');
  let result = [];
  for (let i = 0; i < parts.length; i++) {
    if ((i + 1) % 2 === 0) {
      // even index, unescape double quotes inside the quoted field
      result.push(parts[i].replace(/""/g, '"'));
    } else {
      // odd index, keep as is
      result.push(parts[i]);
    }
  }
  return result.filter(part => part.trim());
}

function toDate(dateStr: string): string | null {
  return dateStr ? new Date(dateStr).toISOString().split('T')[0] : null;
}

function toNumber(str: string): number | null {
  return str ? Number(str.replace(/[^0-9.-]+/g, '')) : null;
}

function toBoolRu(str: string): boolean {
  return ['Да', 'True'].includes(str);
}

function toNullIfEmpty(str: string): string | null {
  return str && str.trim() ? str : null;
}