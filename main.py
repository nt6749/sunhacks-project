import BackBone
import getSummary

def eco_evaluator(array):
    
    result = []
    first = array[0]
    first_eco_score = BackBone.eco_score_calc(first)
    summary_first = getSummary.getSummerization()
    

    for product in array[1:]:
        eco_score = BackBone.eco_score_calc(product)
        result.append({
            "product": product,
            "eco_score": eco_score,})
        
    output = {
        "first_product: ": first,
        "first_eco_score: ": first_eco_score,
        "summary_first: ": summary_first,
        "comparisons: ": result}
    
    return output
    
