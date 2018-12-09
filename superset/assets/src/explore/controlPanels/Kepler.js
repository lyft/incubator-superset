import { t } from '@superset-ui/translation';

export default {
  controlPanelSections: [
    {
      label: t('Query'),
      expanded: true,
      controlSetRows: [
        ['all_columns'],
        ['order_by_cols'],
        ['row_limit', null],
        ['adhoc_filters'],
      ],
    },
    {
      label: t('Advanced'),
      expanded: true,
      controlSetRows: [
        ['autozoom', 'readonly'],
        ['config'],
      ],
    },
  ],
  controlOverrides: {
  },
};
