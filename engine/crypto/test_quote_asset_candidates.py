import unittest
from quote_asset_candidates import candidate_quote_assets, valid_solana_pubkey
class Tests(unittest.TestCase):
 def test_pubkey_canonical_bytes(self):
  self.assertTrue(valid_solana_pubkey('1'*32))
  self.assertTrue(valid_solana_pubkey('So11111111111111111111111111111111111111112'))
  self.assertFalse(valid_solana_pubkey('A'*40))
  self.assertFalse(valid_solana_pubkey('0'*32))
  self.assertFalse(valid_solana_pubkey('1'*33))
 def test_missing(self):
  self.assertEqual(candidate_quote_assets({})['status'],'INSUFFICIENT_METADATA')
 def test_failure(self):
  self.assertEqual(candidate_quote_assets({'meta':{'err':{'InstructionError':[0,'x']},'preTokenBalances':[],'postTokenBalances':[]}})['status'],'FAILED_TRANSACTION')
 def test_candidates_never_claim_verified(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'1'*32,'uiTokenAmount':{'decimals':6}}], 'postTokenBalances':[{'mint':'So11111111111111111111111111111111111111112','uiTokenAmount':{'decimals':9}}]}}
  x=candidate_quote_assets(tx)
  self.assertEqual(len(x['candidates']),2)
  self.assertFalse(x['quote_mint_verified'])
  self.assertFalse(x['fee_entitlement_verified'])
 def test_invalid_decimals(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'1'*32,'uiTokenAmount':{'decimals':True}}], 'postTokenBalances':[]}}
  self.assertEqual(candidate_quote_assets(tx)['candidates'],[])
 def test_conflicting_decimals_fail_closed(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'1'*32,'uiTokenAmount':{'decimals':6}}], 'postTokenBalances':[{'mint':'1'*32,'uiTokenAmount':{'decimals':9}}]}}
  result=candidate_quote_assets(tx)
  self.assertEqual(result['status'],'CONFLICTING_MINT_DECIMALS')
  self.assertEqual(result['candidates'],[])
  self.assertEqual(result['conflicting_mints'],['1'*32])
  self.assertFalse(result['quote_mint_verified'])
 def test_conflict_does_not_remove_other_mints(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'1'*32,'uiTokenAmount':{'decimals':6}},{'mint':'So11111111111111111111111111111111111111112','uiTokenAmount':{'decimals':6}}], 'postTokenBalances':[{'mint':'1'*32,'uiTokenAmount':{'decimals':9}}]}}
  result=candidate_quote_assets(tx)
  self.assertEqual([x['mint'] for x in result['candidates']],['So11111111111111111111111111111111111111112'])
  self.assertEqual(result['status'],'CONFLICTING_MINT_DECIMALS')
if __name__=='__main__':unittest.main()
