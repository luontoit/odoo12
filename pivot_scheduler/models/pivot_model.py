import json
from copy import deepcopy
from functools import reduce
from itertools import product
import datetime
from dateutil.relativedelta import relativedelta

from odoo import _
from odoo.tools.safe_eval import safe_eval


def computeVariation(value, comparisonValue):
    if not value or not computeVariation:
        return
    if comparisonValue == 0:
        if value == 0:
            return 0
        elif value > 0:
            return 1
        else:
            return -1
    return (value - comparisonValue) / abs(comparisonValue)


class PivotModel(object):
    def __init__(self, data=None, env=None):
        self.numbering = {}
        context = data.get('context', '').replace('context_today()', 'datetime.date.today()').replace('.to_utc()', '')
        self.context = safe_eval(context) or {}
        self.initialDomain = safe_eval(data.get('domain', []))
        self.sort = safe_eval(data.get('sort', []))
        self.modelName = data.get('model_id')
        self.env = env
        self.fields = env[self.modelName].fields_get()
        self.data = None

    def _extend_domains(self, d1, d2):
        duplicate = deepcopy(d1)
        if d2:
            duplicate.extend(d2)
        return duplicate

    def sections(self, l):
        sections = []
        for i in range(len(l) + 1):
            sections.append(l[0:i])
        return sections

    def load(self):
        compare = False

        timeRangeMenuData = self.context.get('timeRangeMenuData', {})

        timeRange = timeRangeMenuData.get('timeRange')
        timeRangeDesc = timeRangeMenuData.get('timeRangeDescription')
        if timeRange:
            timeRange = eval(timeRange)

        compTimeRange = timeRangeMenuData.get('comparisonTimeRange')
        compTimeRangeDesc = timeRangeMenuData.get('comparisonTimeRangeDescription')
        if compTimeRange:
            compTimeRange = eval(compTimeRange)
            compare = True

        # domains
        domains = []
        domains.append(self._extend_domains(self.initialDomain, timeRange))
        if compare:
            domains.append(self._extend_domains(self.initialDomain, compTimeRange))

        # origins
        origins = []
        origins.append(timeRangeDesc or "")
        if compare:
            origins.append(compTimeRangeDesc)

        self.data = {
            'domain': self.initialDomain,
            'comparisonField': timeRangeMenuData.get('comparisonField'),
            'timeRange': timeRange,
            'timeRangeDescription': timeRangeDesc,
            'comparisonTimeRange': compTimeRange,
            'comparisonTimeRangeDescription': compTimeRangeDesc,
            'compare': compare,
            'rowGroupBys': self.context.get('pivot_row_groupby', []),
            'colGroupBys': self.context.get('pivot_column_groupby', []),
            'measures': self.context.get('pivot_measures', []),
            'domains': domains,
            'origins': origins,
        }
        sortedColumn = {}
        self.data['sortedColumn'] = sortedColumn
        return self._loadData()

    def _loadData(self):
        self.rowGroupTree = {'root': {'labels': [], 'values': []}, 'directSubTrees': {}}
        self.colGroupTree = {'root': {'labels': [], 'values': []}, 'directSubTrees': {}}
        self.measurements = {}
        self.counts = {}
        self.groupDomains = {}

        key = json.dumps([[], []])
        self.groupDomains[key] = self.data.get('domains')
        group = {'rowValues': [], 'colValues': []}
        leftDivisors = self.sections(self.data.get('rowGroupBys'))
        rightDivisors = self.sections(self.data.get('colGroupBys'))
        divisors = list(product(leftDivisors, rightDivisors))
        self._subdivideGroup(group, divisors[0:1])
        return self._subdivideGroup(group, divisors[1:])

    def _prepareData(self, group, groupSubdivisions):
        groupRowValues = group.get('rowValues')
        groupRowLabels = []
        rowSubTree = self.rowGroupTree
        root = None
        if len(groupRowValues):
            rowSubTree = self._findGroup(self.rowGroupTree, groupRowValues)
            root = rowSubTree.get('root')
            groupRowLabels = root.get('labels')

        groupColValues = group.get('colValues')
        groupColLabels = []
        if len(groupColValues):
            root = self._findGroup(self.colGroupTree, groupColValues).get('root')
            groupColLabels = root.get('labels')
        for groupSubdivision in groupSubdivisions:
            for subGroup in groupSubdivision.get('subGroups'):
                tempGroupRowValues = self._getGroupValues(subGroup, groupSubdivision.get('rowGroupBy'))
                tempGroupRowValues.extend(groupRowValues)
                rowValues = tempGroupRowValues

                tempGroupRowLabels = self._getGroupLabels(subGroup, groupSubdivision.get('rowGroupBy'))
                tempGroupRowLabels.extend(groupRowLabels)
                rowLabels = tempGroupRowLabels

                tempGroupColValues = self._getGroupValues(subGroup, groupSubdivision.get('colGroupBy'))
                tempGroupColValues.extend(groupColValues)
                colValues = tempGroupColValues

                tempGroupColLabels = self._getGroupLabels(subGroup, groupSubdivision.get('colGroupBy'))
                tempGroupColLabels.extend(groupColLabels)
                colLabels = tempGroupColLabels

                if not len(colValues) and len(rowValues):
                    self._addGroup(self.rowGroupTree, rowLabels, rowValues)

                if len(colValues) and not len(rowValues):
                    self._addGroup(self.colGroupTree, colLabels, colValues)

                key = json.dumps([rowValues, colValues])
                originIndex = groupSubdivision.get('group').get('originIndex')

                if not (key in self.measurements):
                    self.measurements[key] = list(
                        map(lambda origin: self._getMeasurements({}), self.data.get('origins')))
                self.measurements[key][originIndex] = self._getMeasurements(subGroup)

                if not (key in self.counts):
                    self.counts[key] = list(map(lambda x: 0, self.data.get('origins')))
                self.counts[key][originIndex] = subGroup.get('__count')

                if not (key in self.groupDomains):
                    self.groupDomains[key] = list(map(lambda x: [[0, '=', 1]], self.data.get('origins')))

                if subGroup.get('__domain'):
                    self.groupDomains[key][originIndex] = subGroup.get('__domain')

    def _subdivideGroup(self, group, divisors):
        key = json.dumps([group.get('rowValues'), group.get('colValues')])

        def _get_reduce(acc, v):
            originIndex = v[0]
            origin = v[1]
            if not self.counts.get(key) or self.counts.get(key)[originIndex] > 0:
                subGroup = {'rowValues': group.get('rowValues'), 'colValues': group.get('colValues'),
                            'originIndex': originIndex}
                for divisor in divisors:
                    acc.append(self._getGroupSubdivision(subGroup, divisor[0], divisor[1]))
            return acc

        groupSubdivisions = reduce(_get_reduce, enumerate(self.data.get('origins')), [])
        if len(groupSubdivisions):
            self._prepareData(group, groupSubdivisions)

    def _getGroupSubdivision(self, group, rowGroupBy, colGroupBy):
        groupDomain = self._getGroupDomain(group) or []
        measureSpecs = self._getMeasureSpecs()
        groupBy = self._extend_domains(rowGroupBy, colGroupBy)

        subGroups = self.env[self.modelName].read_group(domain=groupDomain, fields=measureSpecs, groupby=groupBy,
                                                        lazy=False)
        for subGroup in subGroups:
            for field, value in subGroup.items():
                fieldName = field.split(':')[0]
                if fieldName not in ['__count', '__domain'] and self.fields.get(fieldName, {}).get(
                        'type') == 'many2one':
                    subGroup[field] = self.env[self.fields[fieldName].get('relation')].browse(value[0]).name_get()[0]
        return {
            'group': group,
            'subGroups': subGroups,
            'rowGroupBy': rowGroupBy,
            'colGroupBy': colGroupBy
        }

    def _getGroupDomain(self, group):
        key = json.dumps([group.get('rowValues'), group.get('colValues')])
        return self.groupDomains.get(key, {})[group.get('originIndex')]

    def _getMeasureSpecs(self):
        def _fun_reduce(acc, measure):
            if measure == '__count':
                acc.append(measure)
                return acc
            type = self.fields[measure].get('type')
            groupOperator = self.fields[measure].get('group_operator')
            if type == 'many2one':
                groupOperator = 'count_distinct'
            if groupOperator:
                acc.append(measure + ':' + groupOperator)
            return acc

        return reduce(_fun_reduce, self.data.get('measures'), [])

    def exportData(self):
        self.load()

        measureCount = len(self.data.get('measures'))
        originCount = len(self.data.get('origins'))

        table = self._getTable()

        # process headers
        headers = table.get('headers')
        colGroupHeaderRows = None
        measureRow = []
        originRow = []

        def processHeader(header):
            inTotalColumn = header.get('groupId') and len(header.get('groupId')[1]) == 0 or False
            return {
                'title': header.get('title'),
                'width': header.get('width'),
                'height': header.get('height'),
                'is_bold': not (not header.get('measure')) and inTotalColumn
            }

        if originCount > 1:
            colGroupHeaderRows = headers[0:len(headers) - 2]
            measureRow = list(map(processHeader, headers[len(headers) - 2]))
            originRow = list(map(processHeader, headers[len(headers) - 1]))
        else:
            colGroupHeaderRows = headers[0:len(headers) - 1]
            if measureCount > 1:
                measureRow = list(map(processHeader, headers[len(headers) - 1]))

        # remove the empty headers on left side
        del colGroupHeaderRows[0][0:1]

        colGroupHeaderRows = list(map(lambda headerRow: list(map(processHeader, headerRow)), colGroupHeaderRows))

        # process rows
        def processSubGroupMeasurements(measurement):
            value = measurement.get('value')
            if value is None:
                value = ""
            elif len(measurement.get('originIndexes')) > 1:
                value = value * 100
            return {
                'is_bold': measurement.get('isBold'),
                'value': value,
            }

        def processTableRow(row):
            return {
                'title': row.get('title'),
                'indent': row.get('indent'),
                'values': list(map(processSubGroupMeasurements, row.get('subGroupMeasurements'))),
            }

        tableRows = list(map(processTableRow, table.get('rows')))
        export_data = {
            'col_group_headers': colGroupHeaderRows,
            'measure_headers': measureRow,
            'origin_headers': originRow,
            'rows': tableRows,
            'measure_count': measureCount,
            'origin_count': originCount,
        }
        return export_data

    def _addGroup(self, groupTree, labels, values):
        tree = groupTree
        for val in values[0:len(values) - 1]:
            tree = tree.get('directSubTrees').get(val)
        tree.get('directSubTrees')[values[len(values) - 1]] = {
            'root': {
                'labels': labels,
                'values': values
            },
            'directSubTrees': {},
        }

    def _findGroup(self, groupTree, values):
        tree = groupTree
        for val in values[0:len(values)]:
            tree = tree.get('directSubTrees').get(val)
        return tree

    def _getGroupValues(self, group, groupBys):
        result = []
        for groupBy in groupBys:
            result.append(self._sanitizeValue(group[groupBy]))
        return result

    def _getGroupLabels(self, group, groupBys):
        result = []
        for groupBy in groupBys:
            result.append(self._sanitizeLabel(group[groupBy], groupBy))
        return result

    def _getMeasurements(self, group):
        def _func_reduce(measurements, fieldName):
            measurement = group.get(fieldName)
            if isinstance(measurement, list):
                measurement = 1
            if self.fields.get(fieldName, {}).get('type') == 'boolean' and isinstance(measurement, bool):
                measurement = 1 if measurement else 0
            if len(self.data.get('origins')) > 1 and not measurement:
                measurement = 0
            measurements[fieldName] = measurement
            return measurements

        return reduce(_func_reduce, self.data.get('measures'), {})

    def _sanitizeLabel(self, value, groupBy):
        fieldName = groupBy.split(':')[0]
        if value == False:
            return _("Undefined")
        if isinstance(value, tuple):
            return self._getNumberedLabel(value, fieldName)
        if fieldName and self.fields[fieldName] and (self.fields[fieldName].get('type') == 'selection'):
            selected = filter(lambda s: {0: value}, self.fields[fieldName].get('selection'))[0]
            return selected and selected[1] or value
        return value

    def _sanitizeValue(self, value):
        if isinstance(value, tuple):
            return value[0]
        return value

    def _getNumberedLabel(self, label, fieldName):
        id = label[0]
        name = label[1]
        self.numbering[fieldName] = self.numbering.get('fieldName', {})
        self.numbering[fieldName][name] = self.numbering.get('fieldName', {}).get('name', {})
        numbers = self.numbering[fieldName][name]
        numbers[id] = numbers.get(id) or len(numbers) + 1
        if numbers[id] > 1:
            name += "  (" + numbers[id] + ")"
        return name

    def _getTable(self):
        headers = self._getTableHeaders()
        return {
            'headers': headers,
            'rows': self._getTableRows(self.rowGroupTree, headers[len(headers) - 1]),
        }

    def _getTableHeaders(self):
        colGroupBys = self.data.get('colGroupBys')
        height = len(colGroupBys) + 1
        measureCount = len(self.data.get('measures'))
        originCount = len(self.data.get('origins'))
        leafCounts = self._getLeafCounts(self.colGroupTree)
        headers = []
        measureColumns = []  # used to generate the measure cells

        # 1) generate col group rows (total row + one row for each col groupby)
        colGroupRows = [[] for i in range(height)]
        # blank top left cell
        colGroupRows[0].append({
            'height': height + 1 + (originCount > 1) and 1 or 0,  # + measures rows [+ origins row]
            'title': "",
            'width': 1,
        })

        # col groupby cells with group values
        def generateTreeHeaders(tree):
            group = tree.get('root')
            rowIndex = len(group.get('values'))
            row = colGroupRows[rowIndex]
            groupId = [[], group.get('values')]
            isLeaf = not len(tree.get('directSubTrees'))
            leafCount = leafCounts[json.dumps(tree.get('root').get('values'))]
            cell = {
                'groupId': groupId,
                'height': isLeaf and (len(colGroupBys) + 1 - rowIndex) or 1,
                'isLeaf': isLeaf,
                'title': group.get('labels') and group.get('labels')[len(group.get('labels')) - 1] or _('Total'),
                'width': leafCount * measureCount * (2 * originCount - 1),
            }
            row.append(cell)
            if isLeaf:
                measureColumns.append(cell)
            for subTree in list(tree.get('directSubTrees').values()):
                generateTreeHeaders(subTree)

        generateTreeHeaders(self.colGroupTree)

        # blank top right cell for 'Total' group (if there is more that one leaf)
        if leafCounts[json.dumps(self.colGroupTree.get('root').get('values'))] > 1:
            groupId = [[], []]
            totalTopRightCell = {
                'groupId': groupId,
                'height': height,
                'title': "",
                'width': measureCount * (2 * originCount - 1),
            }
            colGroupRows[0].append(totalTopRightCell)
            measureColumns.append(totalTopRightCell)

        headers.extend(colGroupRows)

        # 2) generate measures row
        measuresRow = self._getMeasuresRow(measureColumns)
        headers.append(measuresRow)

        # 3) generate origins row if more than one origin
        if originCount > 1:
            headers.append(self._getOriginsRow(measuresRow))

        return headers

    def _getTableRows(self, tree, columns):
        rows = []
        group = tree.get('root')
        rowGroupId = [group.get('values'), []]
        title = group.get('labels') and group.get('labels')[len(group.get('labels')) - 1] or _('Total')
        indent = len(group.get('labels'))
        isLeaf = not len(tree.get('directSubTrees'))

        def processSubGroupMeasurements(column):
            colGroupId = column.get('groupId')
            groupIntersectionId = [rowGroupId[0], colGroupId[1]]
            measure = column.get('measure')
            originIndexes = column.get('originIndexes') or [0]

            value = self._getCellValue(groupIntersectionId, measure, originIndexes)

            measurement = {
                'groupId': groupIntersectionId,
                'originIndexes': originIndexes,
                'measure': measure,
                'value': value,
                'isBold': not len(groupIntersectionId[0]) or not len(groupIntersectionId[1]),
            }
            return measurement

        subGroupMeasurements = list(map(processSubGroupMeasurements, columns))

        rows.append({
            'title': title,
            'groupId': rowGroupId,
            'indent': indent,
            'isLeaf': isLeaf,
            'subGroupMeasurements': subGroupMeasurements
        })

        subTreeKeys = tree.get('sortedKeys') or list(tree.get('directSubTrees').keys())
        for subTreeKey in subTreeKeys:
            subTree = tree.get('directSubTrees').get(subTreeKey)
            rows.extend(self._getTableRows(subTree, columns))

        return rows

    def _getLeafCounts(self, tree):
        leafCounts = {}
        leafCount = None

        def processleafCount(acc, subTree):
            subLeafCounts = self._getLeafCounts(subTree)
            leafCounts.update(subLeafCounts)
            return acc + leafCounts[json.dumps(subTree.get('root').get('values'))]

        if not len(tree.get('directSubTrees')):
            leafCount = 1
        else:
            leafCount = reduce(processleafCount, list(tree.get('directSubTrees').values()), 0)

        leafCounts[json.dumps(tree.get('root').get('values'))] = leafCount
        return leafCounts

    def _getMeasuresRow(self, columns):
        sortedColumn = self.data.get('sortedColumn', {})
        measureRow = []

        for column in columns:
            for measure in self.data.get('measures'):
                measureCell = {
                    'groupId': column.get('groupId'),
                    'height': 1,
                    'measure': measure,
                    'title': self.fields.get(measure, {}).get('string'),
                    'width': 2 * len(self.data.get('origins')) - 1,
                }
                if sortedColumn.get('measure') == measure and (sortedColumn.get('groupId') == column.get('groupId')):
                    measureCell['order'] = sortedColumn.get('order')
                measureRow.append(measureCell)
        return measureRow

    def _getOriginsRow(self, columns):
        sortedColumn = self.data.get('sortedColumn', {})
        originRow = []

        for column in columns:
            groupId = column.get('groupId')
            measure = column.get('measure')
            isSorted = sortedColumn.get('measure') == measure and (sortedColumn.get('groupId') == groupId)
            isSortedByOrigin = isSorted and not sortedColumn.get('originIndexes')[1]
            isSortedByVariation = isSorted and sortedColumn.get('originIndexes')[1]

            for originIndex, origin in enumerate(self.data.get('origins')):
                originCell = {
                    'groupId': groupId,
                    'height': 1,
                    'measure': measure,
                    'originIndexes': [originIndex],
                    'title': origin,
                    'width': 1,
                }
                if isSortedByOrigin and sortedColumn.get('originIndexes')[0] == originIndex:
                    originCell['order'] = sortedColumn.get('order')

                originRow.append(originCell)

                if originIndex > 0:
                    variationCell = {
                        'groupId': groupId,
                        'height': 1,
                        'measure': measure,
                        'originIndexes': [originIndex - 1, originIndex],
                        'title': _('Variation'),
                        'width': 1,
                    }
                    if isSortedByVariation and sortedColumn.get('originIndexes')[1] == originIndex:
                        variationCell['order'] = sortedColumn.get('order')
                    originRow.append(variationCell)
        return originRow

    def _getCellValue(self, groupId, measure, originIndexes):
        key = json.dumps(groupId)
        if not self.measurements.get(key):
            return
        values = list(map(lambda originIndex: self.measurements[key][originIndex][measure], originIndexes))
        if len(originIndexes) > 1:
            return computeVariation(values[0], values[1])
        else:
            return values[0]
