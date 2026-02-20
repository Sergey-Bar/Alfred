import { useRef, useState } from 'react';
import api from '../services/api';

export default function ImportExportAdmin() {
    const [message, setMessage] = useState('');
    const userFile = useRef();
    const teamFile = useRef();
    const modelFile = useRef();

    async function handleExport(type) {
        let data = '';
        if (type === 'users') data = await api.exportUsers();
        if (type === 'teams') data = await api.exportTeams();
        if (type === 'models') data = await api.exportModels();
        const blob = new Blob([data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        setMessage(`${type} exported`);
    }

    async function handleImport(type, ref) {
        const file = ref.current.files[0];
        if (!file) return;
        let result;
        if (type === 'users') result = await api.importUsers(file);
        if (type === 'teams') result = await api.importTeams(file);
        if (type === 'models') result = await api.importModels(file);
        setMessage(`${type} import: ${result.imported || 0} imported, ${result.errors?.length || 0} errors`);
    }

    return (
        <div style={{ padding: 24 }}>
            <h2>Import/Export Admin</h2>
            {message && <div style={{ color: 'green', marginBottom: 8 }}>{message}</div>}
            <div style={{ display: 'flex', gap: 32 }}>
                <div>
                    <h3>Users</h3>
                    <button onClick={() => handleExport('users')}>Export Users CSV</button><br />
                    <input type="file" ref={userFile} accept=".csv" />
                    <button onClick={() => handleImport('users', userFile)}>Import Users CSV</button>
                </div>
                <div>
                    <h3>Teams</h3>
                    <button onClick={() => handleExport('teams')}>Export Teams CSV</button><br />
                    <input type="file" ref={teamFile} accept=".csv" />
                    <button onClick={() => handleImport('teams', teamFile)}>Import Teams CSV</button>
                </div>
                <div>
                    <h3>Models</h3>
                    <button onClick={() => handleExport('models')}>Export Models CSV</button><br />
                    <input type="file" ref={modelFile} accept=".csv" />
                    <button onClick={() => handleImport('models', modelFile)}>Import Models CSV</button>
                </div>
            </div>
        </div>
    );
}
