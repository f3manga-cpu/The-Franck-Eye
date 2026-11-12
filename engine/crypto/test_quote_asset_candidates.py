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
if __name__=='__main__':unittest.main()
