#!/usr/bin/env node
// OFFLINE ONLY. Builds a create_v2 instruction. Never loads private keys,
// signs transactions, submits RPC requests, mints, buys or spends SOL.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { PUMP_SDK } = require('@pump-fun/pump-sdk');
const { Keypair, PublicKey } = require('@solana/web3.js');

const ROOT = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
export function getOption(flag) { const i = args.indexOf(flag); return i === -1 ? undefined : args[i+1]; }

export function validate(config) {
  if (typeof config.name !== 'string' || config.name.length === 0 || Buffer.byteLength(config.name, 'utf8') > 32) throw Error('Invalid token name (1-32 bytes)');
  if (typeof config.symbol !== 'string' || config.symbol.length === 0 || Buffer.byteLength(config.symbol, 'utf8') > 13) throw Error('Invalid token ticker (1-13 bytes)');
  if (config.name !== 'Greatest Token Action' || config.symbol !== 'GTA') throw Error('Unexpected brand');
  if (typeof config.description !== 'string' || !config.description.includes('Not affiliated')) throw Error('Independent identity disclaimer required');
  return true;
}
export async function buildPreview({creatorAddress, metadataUri} = {}) {
  const config = JSON.parse(readFileSync(join(ROOT,'token.json'),'utf8'));
  validate(config);
  let creatorMode = 'EPHEMERAL_PREVIEW_ONLY';
  const creator = creatorAddress ? new PublicKey(creatorAddress) : Keypair.generate().publicKey;
  if (creatorAddress) creatorMode='USER_PUBLIC_ADDRESS';
  if (creator.equals(PublicKey.default)) throw Error('Default creator address is not permitted');
  const uri = metadataUri || 'https://example.invalid/gta-metadata.json';
  if (!uri.startsWith('https://') || Buffer.byteLength(uri, 'utf8') > 200) throw Error('Metadata must have an HTTPS URI <=200 bytes');
  const mint = Keypair.generate(); // Ephemeral demo key; deliberately not serialized or retained.
  const instruction = await PUMP_SDK.createV2Instruction({
    mint: mint.publicKey, creator, user: creator,
    name: config.name, symbol: config.symbol, uri,
    mayhemMode: false, holderReward: false,
  });
  return {
    status: 'UNSIGNED_OFFLINE_INSTRUCTION_BUILT',
    broadcast: false, signed: false, amountSpentSol: 0,
    brand: config.name, ticker: config.symbol,
    previewMint: mint.publicKey.toBase58(), previewMintIsNotLaunched: true,
    creator: creator.toBase58(), creatorMode,
    metadataUri: uri,
    metadataIsPlaceholder: !metadataUri,
    programId: instruction.programId.toBase58(),
    accountCount: instruction.keys.length,
    instructionBytes: instruction.data.length,
    signerAddresses: instruction.keys.filter(k=>k.isSigner).map(k=>k.pubkey.toBase58()),
    pendingGates: ['Appropriate creator wallet and owner-controlled signing', 'Permanent verified metadata/image URI', 'Network and rent funding', 'Applicable French/EU issuance and communications review', 'Explicit transaction-level authorization'],
  };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  if (!args.includes('--dry-run')) { console.error('Refusing: only --dry-run is supported.'); process.exit(2); }
  const creatorAddress=getOption('--creator');
  const metadataUri=getOption('--metadata-uri');
  try { console.log(JSON.stringify(await buildPreview({creatorAddress,metadataUri}),null,2)); }
  catch (err) { console.error('CREATE_V2_PREVIEW_FAILED:', err.message); process.exitCode=1; }
}
