import { useState } from 'react';
import '../style/PresenceModal.css';

interface PresenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (name: string) => void;
}

export function PresenceModal({ isOpen, onClose, onConfirm }: PresenceModalProps) {
  const [name, setName] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onConfirm(name);
      setName('');
    }
  };

  return (
    <div className="presence-modal-overlay">
      <div className="presence-modal-card">
        <h2 className="presence-title">Marcar presença</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="name-input">Nome</label>
            <input 
              id="name-input"
              type="text" 
              placeholder="Digite seu nome completo"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
              className="presence-input"
            />
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-cancel">
              Cancelar
            </button>
            <button type="submit" className="btn-confirm" disabled={!name.trim()}>
              Confirmar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}