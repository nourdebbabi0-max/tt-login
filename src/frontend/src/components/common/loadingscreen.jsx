export default function LoadingScreen({ message = "Chargement..." }) {
  return (
    <div className="page-center auth-page-bg">
      <div className="card auth-card">
        <h2>{message}</h2>
      </div>
    </div>
  );
}