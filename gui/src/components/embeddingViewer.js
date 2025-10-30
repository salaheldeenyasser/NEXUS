import React, { useEffect, useState } from "react";

function EmbeddingViewer() {
  const [embeddings, setEmbeddings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/embeddings") // adjust the port if needed
      .then((response) => response.json())
      .then((data) => {
        setEmbeddings(data.embeddings || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching embeddings:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading embeddings...</p>;

  return (
    <div>
      <h2>Loaded Embeddings</h2>
      {embeddings.length === 0 ? (
        <p>No embeddings found.</p>
      ) : (
        <ul>
          {embeddings.map((item, index) => (
            <li key={index}>
              <strong>User ID:</strong> {item.user_id}
              <br />
              <strong>Embedding:</strong> {item.embedding.slice(0, 5).join(", ")}...
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default EmbeddingViewer;
