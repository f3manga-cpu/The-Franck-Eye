import unittest
from quote_asset_candidates import candidate_quote_assets
class Tests(unittest.TestCase):
 def test_missing(self):
  self.assertEqual(candidate_quote_assets({})['status'],'INSUFFICIENT_METADATA')
 def test_failure(self):
  self.assertEqual(candidate_quote_assets({'meta':{'err':{'InstructionError':[0,'x']},'preTokenBalances':[],'postTokenBalances':[]}})['status'],'FAILED_TRANSACTION')
 def test_candidates_never_claim_verified(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'A'*40,'uiTokenAmount':{'decimals':6}}], 'postTokenBalances':[{'mint':'B'*40,'uiTokenAmount':{'decimals':9}}]}}
  x=candidate_quote_assets(tx)
  self.assertEqual(len(x['candidates']),2)
  self.assertFalse(x['quote_mint_verified'])
  self.assertFalse(x['fee_entitlement_verified'])
 def test_invalid_decimals(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'A'*40,'uiTokenAmount':{'decimals':True}}], 'postTokenBalances':[]}}
  self.assertEqual(candidate_quote_assets(tx)['candidates'],[])
 def test_conflicting_decimals_fail_closed(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'A'*40,'uiTokenAmount':{'decimals':6}}], 'postTokenBalances':[{'mint':'A'*40,'uiTokenAmount':{'decimals':9}}]}}
  result=candidate_quote_assets(tx)
  self.assertEqual(result['status'],'CONFLICTING_MINT_DECIMALS')
  self.assertEqual(result['candidates'],[])
  self.assertEqual(result['conflicting_mints'],['A'*40])
  self.assertFalse(result['quote_mint_verified'])
 def test_conflict_does_not_remove_other_mints(self):
  tx={'meta':{'err':None,'preTokenBalances':[{'mint':'A'*40,'uiTokenAmount':{'decimals':6}},{'mint':'B'*40,'uiTokenAmount':{'decimals':6}}], 'postTokenBalances':[{'mint':'A'*40,'uiTokenAmount':{'decimals':9}}]}}
  result=candidate_quote_assets(tx)
  self.assertEqual([x['mint'] for x in result['candidates']],['B'*40])
  self.assertEqual(result['status'],'CONFLICTING_MINT_DECIMALS')
if __name__=='__main__':unittest.main()
