interface BeginScreenProps {
  onStart: () => void; // Uma função que o pai (App) vai passar para saber quando trocar de tela
}

export function BeginScreen({ onStart }: BeginScreenProps) {
  return (
    <div className="home-container">
      <div className="content-wrapper">
        {/* Logo da UFF */}
        <img src="/logo-uff.png" alt="Logo UFF" className="home-logo" />
        
        <div className="text-wrapper">
          <h2 className="university-name">Universidade Federal Fluminense</h2>
          <h1 className="app-title">BusUFF</h1>
        </div>

        {/* Botão de Entrar (ou área clicável) */}
        <button onClick={onStart} className="start-button">
          Acessar Localização
        </button>
      </div>
    </div>
  );
}