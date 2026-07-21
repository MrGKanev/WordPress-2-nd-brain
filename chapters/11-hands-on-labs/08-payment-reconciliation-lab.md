# Lab: Reconcile WooCommerce Payments

This lab compares WooCommerce orders with a payment provider's sandbox records after a controlled test run. It demonstrates why retries and refunds must be reconciled rather than guessed.

## Prepare Test Cases

Create sandbox examples for a successful payment, declined payment, delayed confirmation and refund. Record the WooCommerce order ID and provider payment/refund ID for each case.

| Check | Expected result |
|-------|-----------------|
| Successful payment | Paid order and matching provider capture |
| Declined payment | No fulfilment; provider and order show the correct failure state |
| Delayed webhook | Order updates once when confirmation arrives |
| Refund | Amount and provider refund ID match; stock and email follow policy |

## Reconcile

Compare provider events, WooCommerce order notes, order status, fulfilment state and emails. Investigate before retrying any unclear transaction. A timeout can mean that the provider completed the charge but the store missed the response.

## Completion Criteria

Every test transaction has one clear provider record, one expected WooCommerce state and a documented operator response for an exception. Preserve sandbox evidence for the integration release record.

See [WooCommerce Operations & Integrations](../09-production-workflows/08-woocommerce-operations.md) and [Payment Gateways](../06-e-commerce/05-payment-gateways.md).
