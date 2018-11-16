import { t } from '@superset-ui/translation';
import { ChartMetadata, ChartPlugin } from '@superset-ui/chart';
import transformProps from './transformProps';
import thumbnail from './images/thumbnail.png';

const metadata = new ChartMetadata({
  name: t('Kepler.gl'),
  description: '',
  credits: ['https://github.com/uber/kepler.gl'],
  thumbnail,
});

export default class KeplerChartPlugin extends ChartPlugin {
  constructor() {
    super({
      metadata,
      transformProps,
      loadChart: () => import('./Kepler.jsx'),
    });
  }
}
