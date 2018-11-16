export default function transformProps(chartProps) {
  const { formData, height, width, payload, setControlValue } = chartProps;
  const { mapboxApiAccessToken, features } = payload.data;
  return {
    height,
    width,
    config: formData.config,
    features,
    setControlValue,
    mapboxApiAccessToken,
  };
}
