import { models } from 'powerbi-client';
import { PowerBIEmbed } from 'powerbi-client-react';
import { useEffect, useState } from 'react';

export function App() {
  const [, setReport] = useState<Report | undefined>(undefined);
  const [artifacts, setArtifacts] = useState<{embedUrl: string, accessToken: string }>({embedUrl: '', accessToken: ''});
  
  const fetchPowerBIArtifacts = async () => {
    try {
      const response = await fetch('http://localhost:8000/embed');
      if (!response.ok) throw new Error('Failed to fetch Power BI artifacts');
      const data = await response.json();
      setArtifacts(data);

    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchPowerBIArtifacts();
  }, []);
  return (
      <PowerBIEmbed
        embedConfig = {{
          type: 'report',
          id: import.meta.env.VITE_REPORT_ID as string,
          embedUrl: artifacts.embedUrl,
          accessToken: artifacts.accessToken,
          tokenType: models.TokenType.Embed,
          settings: {
            panes: {
              filters: {
                expanded: false,
                visible: false
              }
            },
            background: models.BackgroundType.Transparent,
          }
        }}
        cssClassName = { "reportClass" }
        getEmbeddedComponent = { (embeddedReport) => {
          setReport(embeddedReport as unknown as Report);
        }}
      />
  )
}


