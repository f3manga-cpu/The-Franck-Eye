import test from 'node:test';
import assert from 'node:assert/strict';
import { validate, buildPreview } from './launch.mjs';
test('name and ticker must remain canonical and in bounds', ()=>{
  const ok={name:'Greatest Token Action',symbol:'GTA',description:'Not affiliated with gaming studios'};
  assert.equal(validate(ok),true);
  assert.throws(()=>validate({...ok,name:'G'.repeat(33)}));
  assert.throws(()=>validate({...ok,symbol:'GTO'}));
  assert.throws(()=>validate({...ok,description:'Unclear'}));
});
test('actual official SDK builds a non-broadcasting instruction with no wallet secrets', async()=>{
  const result=await buildPreview();
  assert.equal(result.status,'UNSIGNED_OFFLINE_INSTRUCTION_BUILT');
  assert.equal(result.signed,false);
  assert.equal(result.broadcast,false);
  assert.equal(result.amountSpentSol,0);
  assert.equal(result.brand,'Greatest Token Action');
  assert.equal(result.metadataIsPlaceholder,true);
  assert.ok(result.instructionBytes>20);
  assert.ok(result.accountCount>=10);
  assert.ok(result.signerAddresses.includes(result.creator));
  assert.ok(result.signerAddresses.includes(result.previewMint));
});
test('invalid external addresses fail closed',async()=>{
  await assert.rejects(buildPreview({creatorAddress:'not-a-wallet'}));
  await assert.rejects(buildPreview({metadataUri:'http://insecure.invalid/json'}));
});
