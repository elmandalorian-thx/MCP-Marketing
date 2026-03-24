"use client";

import { useState } from "react";
import { Topbar } from "@/components/topbar";

interface Client {
  id: string;
  name: string;
  website: string;
  industry: string;
  notes: string;
  createdAt: string;
}

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: "", website: "", industry: "", notes: "" });
  const [search, setSearch] = useState("");

  function addClient() {
    if (!form.name.trim()) return;
    const client: Client = {
      id: Date.now().toString(),
      ...form,
      createdAt: new Date().toISOString(),
    };
    setClients(prev => [client, ...prev]);
    setForm({ name: "", website: "", industry: "", notes: "" });
    setShowAdd(false);
  }

  function removeClient(id: string) {
    setClients(prev => prev.filter(c => c.id !== id));
  }

  const filtered = clients.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.industry.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <Topbar title="Clients" />
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-[0.82rem] text-[#9A9A9A]">{clients.length} client{clients.length !== 1 ? "s" : ""}</p>
          <div className="flex items-center gap-3">
            <input type="text" className="input w-56" placeholder="Search clients..." value={search} onChange={e => setSearch(e.target.value)} />
            <button onClick={() => setShowAdd(!showAdd)} className="btn btn-primary">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
              Add Client
            </button>
          </div>
        </div>

        {/* Add form */}
        {showAdd && (
          <div className="card p-6 mb-6 animate-in">
            <h3 className="text-[0.85rem] font-bold mb-4">New Client</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="input-label">Client Name *</label>
                <input type="text" className="input" placeholder="Acme Corp" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} autoFocus />
              </div>
              <div>
                <label className="input-label">Website</label>
                <input type="text" className="input" placeholder="https://acme.com" value={form.website} onChange={e => setForm(p => ({ ...p, website: e.target.value }))} />
              </div>
              <div>
                <label className="input-label">Industry</label>
                <input type="text" className="input" placeholder="E-commerce, SaaS, etc." value={form.industry} onChange={e => setForm(p => ({ ...p, industry: e.target.value }))} />
              </div>
              <div>
                <label className="input-label">Notes</label>
                <input type="text" className="input" placeholder="Any notes..." value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} />
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={addClient} className="btn btn-success" disabled={!form.name.trim()}>Save Client</button>
              <button onClick={() => { setShowAdd(false); setForm({ name: "", website: "", industry: "", notes: "" }); }} className="btn btn-outline">Cancel</button>
            </div>
          </div>
        )}

        {/* Client list */}
        <div className="card">
          {filtered.length === 0 && clients.length === 0 ? (
            <div className="px-6 py-16 text-center">
              <div className="text-3xl mb-3">👥</div>
              <p className="text-[0.9rem] font-bold text-[#252422] mb-1">No clients yet</p>
              <p className="text-[0.82rem] text-[#9A9A9A] mb-4">Add your first client to organize your marketing work.</p>
              <button onClick={() => setShowAdd(true)} className="btn btn-primary">Add Client</button>
            </div>
          ) : filtered.length === 0 ? (
            <div className="px-6 py-10 text-center text-[0.82rem] text-[#9A9A9A]">
              No clients match &quot;{search}&quot;
            </div>
          ) : (
            <div className="divide-y divide-[#f4f3ef]">
              {filtered.map(client => (
                <div key={client.id} className="px-6 py-4 flex items-center justify-between hover:bg-[#fafaf8] transition-colors group">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#51bcda] to-[#51cbce] flex items-center justify-center text-white font-bold text-sm">
                      {client.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="text-[0.85rem] font-bold text-[#252422]">{client.name}</div>
                      <div className="text-[0.72rem] text-[#9A9A9A] flex items-center gap-3">
                        {client.industry && <span>{client.industry}</span>}
                        {client.website && <a href={client.website} target="_blank" rel="noopener noreferrer" className="text-[#51cbce] hover:underline no-underline">{client.website.replace(/https?:\/\//, "")}</a>}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeClient(client.id)}
                    className="btn btn-outline btn-sm opacity-0 group-hover:opacity-100 transition-all text-[#ef8157] border-[#ef8157]/30"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
