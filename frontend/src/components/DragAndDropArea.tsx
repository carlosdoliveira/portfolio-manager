import { useRef, useState } from "react";

type Props = {
  onFileSelected: (file: File) => void;
};

export function DragAndDropArea({ onFileSelected }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    onFileSelected(files[0]);
  }

  return (
    <div
      className={`dropzone ${isDragging ? "dragging" : ""}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.csv"
        hidden
        onChange={(e) => handleFiles(e.target.files)}
      />

      <div className="dropzone-content">
        <span className="dropzone-icon">📄</span>
        <p>
          <strong>Arraste o arquivo aqui</strong><br />
          ou clique para selecionar
        </p>
        <span className="dropzone-hint">Formatos aceitos: .xlsx, .csv</span>
      </div>
    </div>
  );
}
