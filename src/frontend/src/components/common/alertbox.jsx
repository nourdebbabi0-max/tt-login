export default function AlertBox({ type = "info", message }) {
  if (!message) return null;

  return <div className={`alert-box alert-${type}`}>{message}</div>;
}