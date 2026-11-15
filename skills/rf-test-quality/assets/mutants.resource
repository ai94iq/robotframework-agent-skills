*** Settings ***
Documentation       Mutant checks: a new or changed test must fail when its code or data is broken.
Library             ../scripts/mutation_ledger.py

*** Variables ***
${MUTATION_LOG}     ${OUTPUT_DIR}${/}mutation-ledger.jsonl

*** Keywords ***
Mutant Must Fail
    [Documentation]    Runs ``keyword`` with a mutated input or expectation; it must fail
    ...    on its assertion. A typo or a missing keyword is not a kill.
    ...    Writes one ledger row and returns True when the mutant was killed.
    ...    A survivor is a finding about the check, never a pass.
    [Arguments]    ${test_id}    ${operator}    ${keyword}    @{args}
    ${status}    ${message}=    Run Keyword And Ignore Error    ${keyword}    @{args}
    ${killed}=    Is Kill    ${{$status == 'PASS'}}    ${message}
    Record Mutation    ${MUTATION_LOG}    ${test_id}    ${operator}    ${killed}
    RETURN    ${killed}

Mutation Kill Rate
    [Documentation]    Returns ``{killed, total, rate, survivors}`` read from the ledger.
    ${r}=    Kill Rate    ${MUTATION_LOG}
    RETURN    ${r}
