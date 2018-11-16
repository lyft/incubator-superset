export default function transformProps(chartProps) {
  const { formData, height, width, payload, setControlValue } = chartProps;
  const { mapboxApiAccessToken, features } = payload.data;
  const { config, autozoom } = formData;
  return {
    height,
    width,
    config,
    autozoom,
    features,
    setControlValue,
    mapboxApiAccessToken,
  };
}
